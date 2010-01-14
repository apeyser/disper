##############################################################################
# hook.py - Disper hook system
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

class Hook:
    def __init__(self, version, switcher, cmdline = None):
        self._switcher = switcher
        self._env = os.environ.copy()
        self._env['DISPER_VERSION'] = version
        if cmdline: self._cmdline = cmdline
        # defaults hooks are all user hooks
        self._hooks = ['user']

    '''Set which hooks to call.
       @param hooks list of hook names to call
    '''
    def set_hooks(self, hooks):
        self._hooks = hooks

    '''Call the hooks.
       @param stage action that is happening, one of: 'switch' '''
    def call(self, stage):
        self._env['DISPER_STAGE'] = stage
        self._env['DISPER_LOG_LEVEL'] = logging.getLogger().getEffectiveLevel().__str__()
        self._cmdline = None
        # TODO get current setup

        # and iterate over hooks
        for cmd in self._active_hooks():
            fullcmd = cmd
            if self._cmdline: fullcmd += ' '+self._cmdline
            logging.info('Executing hook: '+fullcmd)
            try: subprocess.Popen(fullcmd, env=self._env).wait()
            except OSError as (errno,strerr): logging.warning('Could not execute hook '+cmd+': '+strerr)

    '''Return full paths of hook programs to call.
       The list of requested hook names is expanded by looking in ~/.disper/hooks and PREFIX/hooks
       for matching executables (excluding prefix). Special hook names 'user' expand to all hooks
       present in ~/.disper/hooks, and 'all' for all hooks present. The order of hooks as specified
       is maintained. A hook name is only called once, even if it appears multiple times in the list.'''
    def _active_hooks(self):
        userhooks = self._get_executables(os.path.join(os.getenv('HOME'),'.disper','hooks'))
        userhooknames = map(lambda x: os.path.splitext(os.path.split(x)[1])[0], userhooks)
        syshooks = [] # TODO self._get_executables(prefix)
        syshooknames = map(lambda x: os.path.splitext(os.path.split(x)[1])[0], syshooks)
        # create list of hook names in same order as specified
        hooks = []
        hooknames = []
        for h in self._hooks:
            if not h:
                # skip empty items
                continue
            elif h == 'user':
                # add new user hooks to list
                for n in range(0,len(userhooks)):
                    if userhooknames[n] not in hooknames:
                        hooks.append(userhooks[n])
                        hooknames.append(userhooknames[n])
            elif h == 'all':
                # add all hooks to list, keeping order
                for n in range(0,len(userhooks)):
                    if userhooknames[n] not in hooknames:
                        hooks.append(userhooks[n]),
                        hooknames.append(userhooknames[n])
                for n in range(0,len(syshooks)):
                    if syshooknames[n] not in hooknames:
                        hooks.append(syshooks[n])
                        hooknames.append(syshooknames[n])
            else:
                # add single hook to list
                if h in hooknames:
                    continue
                elif h in userhooknames:
                    hooknames.append(h)
                    hooks.append(userhooks[userhooknames.index(h)])
                elif h in syshooknames:
                    hooknames.append(h)
                    ooks.append(syshooks[syshooknames.index(h)])
                else: logging.warning('Hook \''+h+'\' requested but not found')
        return hooks

    ''' Return full paths of executable files present in directory'''
    def _get_executables(self, dir):
        hooks = []
        for file in os.listdir(dir):
            path = os.path.join(dir, file)
            if os.path.isfile(path): hooks.append(path)
        return hooks

# vim:ts=4:sw=4:expandtab:
