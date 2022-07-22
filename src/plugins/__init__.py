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
import os

from .hook import Hook


class Plugins:
    def __init__(self, disper):
        """Initialise the plugin system"""
        self.log = logging.getLogger("disper.plugin")
        self.disper = disper
        self._discover()
        self._plugin_names_enabled = []

    def call(self, stage):
        """Call all plugins that are enabled. Must have called #set_enabled first."""
        for plugin in self._plugin_names_enabled:
            self.call_plugin(plugin, stage)

    def call_plugin(self, plugin, stage):
        """Call a plugin by name. Must have called #set_enabled first."""
        self._plugins[plugin].call(stage)

    def set_layout_clone(self, displays, resolution):
        for plugin in self._plugins:
            self._plugins[plugin].set_layout_clone(displays, resolution)

    def set_layout_extend(self, displays, layout, resolutions):
        for plugin in self._plugins:
            self._plugins[plugin].set_layout_extend(displays, layout, resolutions)

    def set_enabled(self, plugins):
        """Set the plugins to be executed.
        @param plugins comma-separated list or Python list of plugin names
               to execute; or 'user' for all user-installed plugins or
               'all' to include all user and system plugins or 'none' for none."""
        if not isinstance(plugins, list):
            plugins = [x.strip() for x in ",".split(plugins)]
        # now expand 'none', 'user' and 'all' plugins
        useplugins = []
        for i in range(len(plugins)):
            if plugins[i] == "none":
                useplugins = []
            elif plugins[i] == "user":
                useplugins += list(self._plugins_user.keys())
            elif plugins[i] == "all":
                useplugins += list(self._plugins.keys())
            elif plugins[i] in list(self._plugins.keys()):
                useplugins.append(plugins[i])
            else:
                self.log.warning("Ignoring nonexistant plugin: " + plugins[i])

        # TODO should we only allow each plugin to be called once?

        self.log.info("Enabled plugins: " + " ".join(useplugins))
        self._plugin_names_enabled = useplugins

    def _discover(self):
        """Create lists of all plugins present"""
        # TODO non-hook plugins
        # find user hooks
        self._plugins_user = {}
        for uhook in self._get_executables(
            os.path.join(os.getenv("HOME"), ".disper", "hooks")
        ):
            name = os.path.splitext(os.path.split(uhook)[1])[0]
            self._plugins_user[name] = Hook(self.disper, uhook)
        self.log.info("Available user hooks: " + ", ".join(self._plugins_user))
        # find system hooks
        self._plugins_system = {}
        for uhook in self._get_executables(
            os.path.join(self.disper.prefix_share, "hooks")
        ):
            name = os.path.splitext(os.path.split(uhook)[1])[0]
            self._plugins_system[name] = Hook(self.disper, uhook)
        self.log.info("Available system hooks: " + ", ".join(self._plugins_user))

        # Now create global list of plugins where user plugins get precedence
        self._plugins = {}
        for i in self._plugins_system:
            self._plugins[i] = self._plugins_system[i]
        for i in self._plugins_user:
            self._plugins[i] = self._plugins_user[i]

    def _get_executables(self, directory):
        """Return full paths of executable files present in directory"""
        hooks = []
        if os.path.isdir(directory):
            for f in os.listdir(directory):
                path = os.path.join(directory, f)
                if os.path.isfile(path):
                    hooks.append(path)
        return hooks
