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

import logging
from plugin import Plugin

class Hook(Plugin):
    '''A hook is a plugin that executes an external command'''

    def __init__(self, disper):
        self.super(disper)
        self._env = os.environ.copy()
        self._env['DISPER_VERSION'] = self.disper.version

    def call(self, stage):
        self._env['DISPER_STAGE'] = stage
        self._env['DISPER_LOG_LEVEL'] = logging.getLogger().getEffectiveLevel().__str__()


# vim:ts=4:sw=4:expandtab:
