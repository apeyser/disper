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
        '''return a set of supported resolutions for a display.
        Displays need to be associated to probe their modelines, so this method
        temporarily changes that (and reverts to the old setup before
        returning).'''

        # Get display resolutions for all displays. The display needs to have
        # it associated to the X screen to be able to do this. So we check that
        # it is associated first and do so when needed. Restore associated
        # displays afterwards.
        # Note: When twinview has not been enabled before, the X server can
        #       *crash* when a display is associated that isn't mentioned in
        #       any metamode line. So create an autoselect modeline first.
        olddisplays = self.nv.get_screen_associated_displays(self.screen)
        assocdisplays = set(olddisplays).union(set([ndisp]))
        if set(olddisplays) != set(assocdisplays):
            oldid = self._add_metamode_autoselect(assocdisplays)
            self._set_associated_displays(assocdisplays)

        self.nv.build_modepool(self.screen, ndisp)
        resolutions = set()
        for m in self.nv.get_display_modelines(self.screen, ndisp):
            r = re.search(r'::\s*"(\d+x\d+)"', m)
            if not r: continue
            resolutions.add(r.group(1))
        self.log.info('resolutions of %s: %s'%(ndisp, ', '.join(resolutions)))

        if set(olddisplays) != set(assocdisplays):
            if oldid > 0: self._delete_metamode(oldid)
            self._set_associated_displays(olddisplays)

        return resolutions


    def switch_clone(self, res, displays=None):
        '''switch to resolution and clone all displays'''

        if not displays:
            displays = self.get_displays()

        # set scaling modes to aspect-ratio scaled
        # this fails if it's done for all of them at once, so do it separately
        for d in displays:
            self.nv.set_screen_scaling(self.screen, d, 'best fit', 'aspect scaled')

        # create new MetaMode and associate displays
        oldid = self._add_metamode_autoselect(displays)
        assocdisplays = self.nv.get_screen_associated_displays(self.screen)
        assocdisplays = set(assocdisplays).union(set(displays))
        self._set_associated_displays(assocdisplays)
        mmid = self._find_metamode_clone(res, displays)
        if mmid < 0:
            mmid = self._add_metamode_clone(res, displays)
        if oldid > 0: self._delete_metamode(oldid)

        # change to this mode using xrandr and refresh as id
        self._xrandr_switch(res, mmid)

        # delete dangling metamodes and deassociate old
        self._cleanup_metamodes(displays)
        self._set_associated_displays(displays)


    def _find_metamode_clone(self, res, displays = None):
        '''find the id of an existing clone metamode for a specific resolution'''
        foundid = -1
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

            if found:
                if foundid > 0:
                    self.log.warning('multiple matching modes found: %s'%res)
                foundid = int(id)

        return foundid


    def _add_metamode_clone(self, res, displays):
        '''add a metamode that clones all displays at the specified resolution.
        Also these displays will be associated to the X screen.'''
        ## To enter a MetaMode line, the displays involved must have been
        ## associated or the nvidia driver doesn't remember display names.
        mm = ', '.join(map(lambda d: '%s: %s +0+0'%(d,res), displays))
        self.log.info('adding metamode: %s'%mm)
        return self.nv.add_screen_metamode(self.screen, mm)


    def _add_metamode_autoselect(self, displays):
        '''add a temporary auto-select metamode that is needed before
        associating displays. returns id of created mode, or -1 if it
        already existed'''
        ## There must be a metamode containing all displays when associating
        ## displays, or the X server may crash.
        mm = ', '.join(map(lambda d: '%s: nvidia-auto-select'%d, displays))
        self.log.info('adding auto-select metamode: %s'%mm)
        return self.nv.add_screen_metamode(self.screen, mm)


    def _delete_metamode(self, id):
        '''delete the specified metamode.'''
        self.log.info('deleting metamode: %d'%id)
        return self.nv.delete_screen_metamode(self.screen, id)


    def _set_associated_displays(self, displays, dodelete = False):
        '''set the displays associated to the current X screen. Dangling
        metamodes are deleted before switching if dodelete is True.'''
        # associate displays
        self.log.info('associating displays: %s'%(', '.join(displays)))
        return self.nv.set_screen_associated_displays(self.screen, displays)


    def _xrandr_switch(self, res, mmid):
        '''switch to the specified MetaMode id'''
        screen = xrandr.get_current_screen()
        sizeidx = None
        w,h = res.split('x')
        for i,s in enumerate(screen.get_available_sizes()):
            if int(s.width) == int(w) and int(s.height) == int(h):
                sizeidx = i
        if sizeidx == None or sizeidx == -1:
            raise Exception( 'could not set display mode: resolution not found (this is a bug)' )
        screen.set_size_index(sizeidx)
        screen.set_refresh_rate(mmid)
        logging.info('switching to metamode %d: [%d] %s / %s'%(mmid,sizeidx,res,mmid))
        screen.apply_config()


    def _cleanup_metamodes(self, displays):
        '''cleanup metamodes referencing displays that are not associated.
        driver loses display names in metamodes when displays are not
        associated and they remain around. Some more details to be found on
          http://www.nvnews.net/vbulletin/showthread.php?t=123781
        It is important that all displays currently present in the metamode
        list are associated to the X screen.
        '''
        metamodes = self.nv.get_metamodes(self.screen)
        for mm in metamodes:
            r = re.match(r'\s*id=(\d+).*::\s*(.*)$', mm)
            if not r: continue
            id, line = int(r.group(1)), r.group(2)
            for i,dc in enumerate(line.split(',')):
                r = re.match(r'^\s*([^:]*)\s*:\s*(.*?)\s*$', dc)
                if not r: continue
                disp, mm = r.group(1), r.group(2)
                if not disp in displays and mm != 'NULL':
                    self.log.info('deleting dangling metamode %d: %s'%(id,line))
                    self.nv.delete_screen_metamode(self.screen, line)


# vim:ts=4:sw=4:expandtab:
