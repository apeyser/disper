# swxrandr.py - display switching using XRandR

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

import logging

import xrandr

from .resolutions import *


class XRandrSwitcher:
    def __init__(self):
        self.log = logging.getLogger("disper.switcher.xrandr")
        self.screen = xrandr.get_current_screen()
        if not xrandr.has_extension():
            raise Exception("No XRandR extension found")

    def get_displays(self):
        """return an array of connected displays"""
        displays = self.screen.get_outputs()
        displays = [o for o in displays if o.is_connected()]
        displays = [o.name for o in displays]
        return displays

    def get_primary_display(self):
        # no idea, just return first one for now
        return self.get_displays()[0]

    def get_display_name(self, ndisp):
        """return the name of a display"""
        # nothing more as of now
        return ndisp

    def get_display_supported_res(self, ndisp):
        """return a set of supported resolutions for a display."""
        o = self.screen.get_output_by_name(ndisp)
        return o.get_available_resolutions()

    def get_display_preferred_res(self, ndisp):
        """return the preferred resolution for a display."""
        o = self.screen.get_output_by_name(ndisp)
        m = o.get_available_modes()[o.get_preferred_mode()]
        return [m.width, m.height]

    def get_display_edid(self, ndisp):
        """return the EDID data for a display."""
        # not available now
        return None

    def switch_clone(self, displays, res):
        """switch to resolution and clone all displays"""
        ress = ResolutionSelection(res, displays)
        return self._switch(displays, ress, xrandr.RELATION_SAME_AS)

    def switch_extend(self, displays, direction, ress):
        """extend desktop across all displays. direction is one of
        'left'/'right'/'bottom'/'top', and ress a dict of a resolution
        for each display."""
        relation = None
        if direction == "left":
            relation = xrandr.RELATION_LEFT_OF
        elif direction == "right":
            relation = xrandr.RELATION_RIGHT_OF
        elif direction == "top":
            relation = xrandr.RELATION_ABOVE
        elif direction == "bottom":
            relation = xrandr.RELATION_BELOW
        else:
            raise ValueError("extend direction must be left/right/bottom/top")
        return self._switch(displays, ress, relation)

    def import_config(self, cfg):
        """restore a display configuration as exported by export_config()"""
        raise NotImplementedError("import not yet implemented")

    def export_config(self):
        """return a string that contains all information to set the current
        display configuration using import_config()."""
        raise NotImplementedError("export not yet implemented")

    def _switch(self, displays, ress, relation):
        """switch displays to the specified resolution according to XRandR relation"""
        dprev = None
        old_displays = self.get_displays()
        for d in displays:
            res = ress[d]
            s = res.size()
            # for each display, select mode with highest refresh rate at res
            o = self.screen.get_output_by_name(d)
            modes = []
            for i, mode in enumerate(o.get_available_modes()):
                if mode.width != s[0]:
                    continue
                if mode.height != s[1]:
                    continue
                refresh = mode.dotClock / (mode.hTotal * mode.vTotal)
                modes.append([i, refresh])
            modes.sort(key=lambda x: x[1])
            if len(modes) > 1:
                self.log.info(
                    str(d)
                    + ": available refresh rates for resolution "
                    + str(res)
                    + ": "
                    + ", ".join(["%d" % (o[1]) for o in modes])
                )
            if len(modes) == 0:
                raise ValueError(
                    "Mode %dx%d is invalid for display %s" % (s[0], s[1], d)
                )
            mode = modes[-1]
            self.log.info(
                str(d)
                + ": selecting XRandR mode #%d: %s %dHz" % (mode[0], res, mode[1])
            )
            o.set_to_mode(mode[0])
            if dprev:
                o.set_relation(dprev, relation)
            dprev = d
            if d in old_displays:
                old_displays.remove(d)

        if len(old_displays) > 0:
            for d in old_displays:
                o = self.screen.get_output_by_name(d)
                o.disable()

        self.screen.apply_output_config()

    def set_scaling(self, displays, scaling):
        if scaling == "default":
            return
        raise NotImplementedError("scaling not implemented for XRandR")
