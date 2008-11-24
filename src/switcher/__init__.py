##############################################################################
# __init__.py - display switching with multiple backends
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

# backends
from swnvidia import NVidiaSwitcher

_backends = [NVidiaSwitcher]

class Switcher:

	backend = None

	def __init__(self):
		'''Initialise the switcher and find a backend'''
		self._probe_backend()

	def _probe_backend(self):
		'''Find and instantiate a suitable backend'''
		self.backend = None
		for b in _backends:
			try:
				self.backend = b()
			except Exception,e:
				continue
			break
		if not self.backend:
			raise Exception('No supported video card found')

	def __getattr__(self, name):
		'''Pass unrecognised methods to the switcher itself; this is to
		simulate binding to a parent class at runtime.'''
		return getattr(self.backend, name)

