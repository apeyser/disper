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

    def get_display_name(self, ndisp):
        '''return the name of a display'''
        return self.nv.get_display_name(self.screen, ndisp)

    def get_display_res(self, ndisp):
        '''return an array of supported resolutions for a display'''
        # Get display resolutions. The display needs to have it associated to
        # the X screen to be able to do this. So we check that it is associated
        # first and do so when needed. Restore associated displays afterwards.
        newass = oldass = set(self.nv.get_screen_associated_displays(self.screen))
        newass.add(ndisp)
        self.nv.set_screen_associated_displays(self.screen, newass)
        self.nv.build_modepool(self.screen, ndisp)
        modelines=self.nv.get_display_modelines(self.screen, ndisp)
        self.nv.set_screen_associated_displays(self.screen, oldass)

        res = set()
        for m in modelines:
            r = re.search(r'::\s*"(\d+x\d+)"', m)
            if not r: continue
            res.add(r.group(1))

        return res

    def switch_clone(self, res, displays=None):
        '''switch to resolution and clone all displays'''

        if not displays:
            displays = self.get_displays()

        # set scaling modes to aspect-ratio scaled
        # this fails if it's done for all of them at once, so do it separately
        for d in displays:
            self.nv.set_screen_scaling(self.screen, d, 'best fit', 'aspect scaled')

        # find suitable metamode, or create one if needed
        mmid = self._find_metamode_clone(res)
        if mmid < 0:
            mm = ', '.join([res+'+0+0']*len(displays))
            self.log.info('adding metamode: %s'%mm)
            self.nv.add_screen_metamode(self.screen, mm)
            mmid = self._find_metamode_clone(res)

        # enable all displays
        # this must be put _after_ metamode creation or the Xorg driver restarts
        ret = self.nv.set_screen_associated_displays(self.screen, displays)
        if not ret:
            self.log.error('could not attach displays to screen #%d: %s'%(self.screen, str(displays)))

        # change to this mode using xrandr and refresh as id
        screen = xrandr.get_current_screen()
        sizeidx = None
        w,h = res.split('x')
        for i,s in enumerate(screen.get_available_sizes()):
            if int(s.width) == int(w) and int(s.height) == int(h):
                sizeidx = i
        if sizeidx == None:
            raise SystemExit( "Could not set display mode: resolution not found (this is a bug)" )
        self.log.info('setting xrandr: (%d) %s / %d'%(sizeidx, res, mmid))
        screen.set_size_index(sizeidx)
        screen.set_refresh_rate(mmid)
        screen.apply_config()


    def _find_metamode_clone(self, res):
        '''find the id of an existing clone metamode for a specific resolution'''
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
                # than connected monitors, require them to be disabled (NULL).
                # XXX this assumes that currently active monitors are shown first. For
                #     laptops this might be expected, but in general _not_ !!!
                if i < len(displays):
                    r = re.match(r'[^:]+:\s*'+res+'(\s+@'+res+')?\s+\+0\+0', dc.strip())
                else:
                    r = re.match(r'[^:]+:\s*NULL',dc.strip())
                if not r: found = False
            if found: return int(id)

        return -1


# vim:ts=4:sw=4:expandtab:
