##############################################################################
# plugin.py - disper plugin
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#        
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License at http://www.gnu.org/licenses/gpl.txt
# By using, editing and/or distributing this software you agree to
# the terms and conditions of this license.

import os
import logging
import subprocess
from plugin import Plugin

class Hook(Plugin):
    '''A hook is a plugin that executes an external command'''

    def __init__(self, disper, script=None):
        Plugin.__init__(self, disper)
        if script: self.set_script(script)
        self._env = os.environ.copy()
        self._env['DISPER_VERSION'] = self.disper.version

    def set_script(self, script):
        '''set the script to execute'''
        self._script = script
        self.log = logging.getLogger('disper.plugin.hook.'+os.path.basename(script))

    def set_layout_clone(self, displays, resolution):
        displays = self._translate_displays(displays)
        self._env['DISPER_DISPLAYS'] = ' '.join(displays)
        self._env['DISPER_LAYOUT'] = 'clone'
        self._env['DISPER_BB_RESOLUTION'] = str(resolution)
        for d in displays:
            self._env['DISPER_RESOLUTION_'+d] = str(resolution)
            self._env['DISPER_POSITION_'+d] = '0,0'

    def set_layout_extend(self, displays, layout, resolutions):
        hdisplays = self._translate_displays(displays)
        self._env['DISPER_DISPLAYS'] = ' '.join(hdisplays)
        self._env['DISPER_LAYOUT'] = layout
        bb = [0,0]
        for i in range(len(displays)):
            # TODO move computation to switcher/resolutions.py:ResolutionSelection
            r = resolutions[displays[i]].size()
            if layout in ['right','left']:
                bb[0] += r[0]
                bb[1] = max(bb[1], r[1])
            else:
                bb[1] += r[1]
                bb[0] = max(bb[0], r[0])
            self._env['DISPER_RESOLUTION_'+hdisplays[i]] = str(resolutions[displays[i]])
            self._env['DISPER_POSITION_'+hdisplays[i]] = '' # TODO
        self._env['DISPER_BB_RESOLUTION'] = 'x'.join(map(str, bb))

    def call(self, stage):
        '''Call the hook'''
        self._env['DISPER_STAGE'] = stage
        self._env['DISPER_LOG_LEVEL'] = self.log.getEffectiveLevel().__str__()
        cmd = [self._script] + self.disper.argv
        self.log.info('Executing hook: '+' '.join(cmd))
        try: subprocess.Popen(cmd, env=self._env).wait()
        except OSError, e: self.log.warning('Could not execute hook '+self._script+': '+ e.strerror)

    def _translate_displays(self, displays):
        '''replace invalid variable name characters for displays'''
        return map(lambda d: d.replace('-','_'), displays)

# vim:ts=4:sw=4:expandtab:
