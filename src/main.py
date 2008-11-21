#!/usr/bin/env python

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

from switcher_nvidia import NVidiaSwitcher


def get_resolutions(sw):
    '''return an array of resolution-sets for each display connected'''
    res = []
    for ndisp in range(sw.get_displays()):
        print 'display #%d: %s'%(ndisp, sw.get_display_name(ndisp))
        res.append(sw.get_display_res(ndisp))
        if len(res[-1])==0:
            print 'WARNING: no resolutions found for display, falling back to default'
            res[-1] = set(['800x600','640x480'])
    return res


def get_common_resolutions(res):
    '''return a list of common resolutions from an array of resolution-sets
    as returned by get_resolutions(). return value is sorted from high to
    low.'''
    commonres = res[0]
    for n in range(1,len(res)):
        commonres.intersection_update(res[n])
    commonres = list(commonres)
    commonres.sort(lambda x,y: int(y.partition('x')[0]) - int(x.partition('x')[0]))
    return commonres


if __name__ == "__main__":
    nv = NVidiaSwitcher()
    res = get_resolutions(nv)
    commonres = get_common_resolutions(res)
    if len(commonres)==0:
        print 'ERROR: displays share no common resolution'
    else:
        nv.switch_clone(commonres[0])

# vim:ts=4:sw=4:expandtab:
