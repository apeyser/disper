##############################################################################
# __init__.py - disper plugin system
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
from hook import Hook
from plugin import Plugin

class Plugins:

    def __init__(self, disper):
        '''Initialise the plugin system'''
        self.log = logging.getLogger('plugins')
        self.disper = disper

    def call(self, stage):
        '''Call all plugins that are enabled'''
        # TODO

# vim:ts=4:sw=4:expandtab:
