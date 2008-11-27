##############################################################################
# switcher-nvidia.py - display switching for nVidia cards
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
        
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License at http://www.gnu.org/licenses/gpl.txt
# By using, editing and/or distributing this software you agree to
# the terms and conditions of this license.

import re
import logging

import xrandr

import nvidia

class NVidiaSwitcher:

    nvidia = None
    displays = None
    _resolutions = None

    def __init__(self):
        self.nv = nvidia.NVidiaControl()
        self.screen = nvidia.Screen(self.nv.xscreen)
        self.log = logging.getLogger('nVidia')

    def get_displays(self):
        '''return an array of connected displays'''
        if self.displays:
            return self.displays

        self.displays = self.nv.probe_displays(self.screen)
        return self.displays

    def get_primary_display(self):
        '''return the primary display of this system. I'm not really sure how
        to do this, so currently the first found flat panel display (DFP) is
        returned, or CRT if none, or TV if neither.'''
        displays = self.get_displays()
        for d in ['DFP', 'CRT', 'TV']:
            for i in range(8):
                disp = '%s-%1d'%(d,i)
                if disp in displays:
                    return disp
        # this should be unreachable code, but be safe
        self.error('program error, could not determine primary display')
        return displays[0]

    def get_display_name(self, ndisp):
        '''return the name of a display'''
        return self.nv.get_display_name(self.screen, ndisp)

    def get_display_res(self, ndisp):
        '''return a set of supported resolutions for a display. All displays
        are queried on first call, subsequent calls return cached information.
        Displays need to be associated to probe their modelines, so this method
        temporarily changes that (and reverts to the old setup before
        returning).'''
        if self._resolutions:
            if not ndisp in self._resolutions:
                raise ValueError('Cannot detect resolutions: display %s not connected'%str(ndisp))
            return self._resolutions[ndisp]

        self._resolutions = {}

        # Get display resolutions for all displays. The display needs to have
        # it associated to the X screen to be able to do this. So we check that
        # it is associated first and do so when needed. Restore associated
        # displays afterwards.
        # Note: When twinview has not been enabled before, the X server can
        #       *crash* when a display is associated that isn't mentioned in
        #       any metamode line.
        olddisps = self.nv.get_screen_associated_displays(self.screen)
        alldisps = self.get_displays()
        if set(olddisps) != set(alldisps):
            self._add_metamode_clone('nvidia-auto-select', alldisps)
        for d in alldisps:
            self.nv.build_modepool(self.screen, d)
            self._resolutions[d] = set()
            for m in self.nv.get_display_modelines(self.screen, d):
                r = re.search(r'::\s*"(\d+x\d+)"', m)
                if not r: continue
                self._resolutions[d].add(r.group(1))
            self.log.info('resolutions of %s: %s'%(d, ', '.join(self._resolutions[d])))

        if set(olddisps) != set(alldisps):
            self._set_associated_displays(olddisps)

        return self.get_display_res(ndisp)

    def switch_clone(self, res, displays=None):
        '''switch to resolution and clone all displays'''

        if not displays:
            displays = self.get_displays()

        # set scaling modes to aspect-ratio scaled
        # this fails if it's done for all of them at once, so do it separately
        for d in displays:
            self.nv.set_screen_scaling(self.screen, d, 'best fit', 'aspect scaled')

        # make sure we have a suitable metamode
        self._add_metamode_clone(res, displays)
        mmid = self._find_metamode_clone(res, displays)

        # change to this mode using xrandr and refresh as id
        screen = xrandr.get_current_screen()
        sizeidx = None
        w,h = res.split('x')
        for i,s in enumerate(screen.get_available_sizes()):
            if int(s.width) == int(w) and int(s.height) == int(h):
                sizeidx = i
        if sizeidx == None or sizeidx == -1:
            raise Exception( 'could not set display mode: resolution not found (this is a bug)' )
        self.log.info('switching to metamode %d using XRandR: [%d] %s / %d'%(mmid, sizeidx, res, mmid))
        screen.set_size_index(sizeidx)
        screen.set_refresh_rate(mmid)
        screen.apply_config()


    def _find_metamode_clone(self, res, displays = None):
        '''find the id of an existing clone metamode for a specific resolution'''
        if not displays:
            displays = self.get_displays()
        metamodes = self.nv.get_metamodes(self.screen)
        for mm in metamodes:
            r = re.match(r'\s*id=(\d+).*::\s*(.*)$', mm)
            if not r: continue
            id = r.group(1)
            found = True
            for i,dc in enumerate(r.group(2).split(',')):
                # Every display must have real and virtual resolution requested with an
                # origin at (0,0) - that's clone. When metamodes contain more entries
                # than specified monitors, require them to be disabled (NULL).
                r = re.match(r'^\s*([^:]*)\s*:\s*(.*?)\s*$', dc)
                if not r:
                    found = False
                    continue
                disp, mm = r.group(1), r.group(2)
                if disp in displays:
                    r = re.match('^\s*'+res+'(\s+@'+res+')?\s+\+0\+0\s*$', mm)
                    if not r: found = False
                else:
                    r = re.match('^\s*NULL\s*$', mm)
                    if not r: found = False

            if found: return int(id)

        return -1

    def _add_metamode_clone(self, res, displays):
        '''add a metamode that clones all displays at the specified resolution.
        Also these displays will be associated to the X screen.'''
        # TODO error checking
        ## There must be a metamode containing all displays when associating
        ## displays, or the X server may crash.
        ## To enter a MetaMode line, the displays involved must have been
        ## associated or the nvidia driver doesn't remember display names.
        # dummy metamode to enable association
        mm = ', '.join(map(lambda d: '%s: nvidia-auto-select +0+0'%d, displays))
        self.log.info('adding auto-select metamode: %s'%mm)
        self.nv.add_screen_metamode(self.screen, mm)
        # associate
        self._set_associated_displays(displays)
        # now the real metamode
        if res != 'nvidia-auto-select':
            mm = ', '.join(map(lambda d: '%s: %s +0+0'%(d,res), displays))
            self.log.info('adding metamode: %s'%mm)
            self.nv.add_screen_metamode(self.screen, mm)

    def _set_associated_displays(self, displays):
        '''set the displays associated to the current X screen.'''
        # associate displays
        self.log.info('associating displays: %s'%(', '.join(displays)))
        return self.nv.set_screen_associated_displays(self.screen, displays)


# vim:ts=4:sw=4:expandtab:
