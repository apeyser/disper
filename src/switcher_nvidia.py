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
import sys

import xrandr

import xnet
import minx
import nvctrl

class NVidiaSwitcher:

    # NV-CONTROL
    xsock        = None
    xconn        = None
    xscreen        = None
    NVCtrl        = None
    nvctrlv        = (0,0)
    gpucount    = 0

    ngpu        = 0 # default gpu number

    def __init__(self):
        self.init_NV_CONTROL()
        self.validate_GPU_count()

    def get_displays(self):
        '''return the number of connected displays'''
        displays = self.get_GPU_displays(self.ngpu)
        return len(displays)

    def get_display_name(self, ndisp):
        '''return the name of a display'''
        displays = self.get_GPU_displays(self.ngpu)
        ndisp = displays[ndisp]
        return nvctrl.get_GPU_display_name( self.xsock, self.NVCtrl.major_opcode, self.ngpu, ndisp )

    def get_display_res(self, ndisp):
        '''return an array of supported resolutions for a display'''
        displays = self.get_GPU_displays(self.ngpu)
        ndisp = displays[ndisp]

        # enable display
        nvctrl.build_GPU_modepool( self.xsock, self.NVCtrl.major_opcode, self.ngpu, ndisp )

        modelines=nvctrl.get_GPU_display_modelines( self.xsock, self.NVCtrl.major_opcode, self.ngpu, ndisp )
        res = set()
        for m in modelines:
            r = re.search(r'::\s*"(\d+x\d+)"', m)
            if not r: continue
            res.add(r.group(1))
        return res

    def switch_clone(self, res):
        '''switch to resolution and clone all displays'''
        # enable displays
        displays = self.get_GPU_displays(self.ngpu)

        # set scaling modes to aspect-ratio scaled
        # this fails if it's done for all of them at once, so do it separately
        for d in displays:
            nvctrl.set_screen_scaling( self.xsock, self.NVCtrl.major_opcode, self.xscreen, [d], 2, 3)

        # find suitable metamode, or create one if needed
        mmid = self._find_metamode_clone(res)
        if mmid < 0:
            mm = ', '.join([res+'+0+0']*len(displays))
            self.info('adding metamode: %s'%mm)
            nvctrl.add_screen_metamode( self.xsock, self.NVCtrl.major_opcode, self.xscreen, mm )
            mmid = self._find_metamode_clone(res)

        # enable all displays
        # this must be put _after_ metamode creation or the Xorg driver restarts
        ret = nvctrl.set_screen_associated_displays( self.xsock, self.NVCtrl.major_opcode, self.xscreen, displays )
        if not ret:
            self.info('ERROR: could not attach displays to screen #%d: %s'%(self.xscreen, str(displays)))

        # change to this mode using xrandr and refresh as id
        screen = xrandr.get_current_screen()
        sizeidx = None
        w,h = res.split('x')
        for i,s in enumerate(screen.get_available_sizes()):
            if int(s.width) == int(w) and int(s.height) == int(h):
                sizeidx = i
        if sizeidx == None:
            raise SystemExit( "Could not set display mode: resolution not found (this is a bug)" )
        self.info('setting xrandr: [%d] %s / %d'%(sizeidx, res, mmid))
        screen.set_size_index(sizeidx)
        screen.set_refresh_rate(mmid)
        screen.apply_config()


    def _find_metamode_clone(self, res):
        '''find the id of an existing clone metamode for a specific resolution'''
        displays = self.get_GPU_displays(self.ngpu)
        metamodes = nvctrl.get_screen_metamodes( self.xsock, self.NVCtrl.major_opcode, self.xscreen )
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

    def info(self, str):
        print '[nVidia] '+str


###############################################################################
# NV-CONTROL
#

    def validate_GPU_count(self):
        '''count GPUs and make sure there is at least 1.
        bail if no Nvidia GPUs are found'''

        self.gpucount = 0
        try:
            self.gpucount = nvctrl.get_GPU_count( self.xsock, self.NVCtrl.major_opcode )
        except Exception,e:
            raise SystemExit( "Error counting GPU's:" + str(e) )
        else:
            if self.gpucount == 0:
                raise SystemExit( "GPU count = 0" )


    def get_GPU_displays(self, ngpu):
        '''return an array of display numbers attached to a GPU'''
        try:
                displays = nvctrl.get_GPU_displays( self.xsock, self.NVCtrl.major_opcode, ngpu )
        except Exception,e:
            raise SystemExit( 'Error getting attached displays: ' + str(e) )
        return displays


    def init_NV_CONTROL(self):
        '''connect to X and confirm NV-CONTROL. bail if X chokes, no NV-CONTROL
        is found, or the buggy NV-CONTROL (minor 9 or 8) is found'''

        try:
            name, host, displayno, self.xscreen = xnet.get_X_display()
            self.xsock, self.xconn = minx.XConnect()
            self.NVCtrl = minx.XQueryExtension( self.xsock, 'NV-CONTROL' )
        except Exception,e:
            raise SystemExit( 'Error connecting to X or querying extensions: ' + str(e) )

        if not self.NVCtrl.present:
            self.xsock.close()
            raise SystemExit( 'NV-CONTROL not found' )

        try:
            self.nvctrlv = nvctrl.get_NV_CONTROL_version( self.xsock,self.NVCtrl.major_opcode )
        except Exception,e:
            raise SystemExit( 'Error checking NV-CONTROL version: ' + str(e) )

        if self.nvctrlv[1] == 8 or self.nvctrlv[1] == 9:
            self.xsock.close()
            raise SystemExit( 'NV-CONTROL arg swap bug. Minor version = %i' % self.nvctrlv[1] )

# vim:ts=4:sw=4:expandtab:
