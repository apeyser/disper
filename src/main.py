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

import sys
import logging
import optparse

from switcher_nvidia import NVidiaSwitcher


# program name and version
progname = 'disper'
progver = '0.1'


def get_resolutions(sw):
    '''return an array of resolution-sets for each display connected'''
    res = []
    for ndisp in range(sw.get_displays()):
        logging.info('display #%d: %s'%(ndisp, sw.get_display_name(ndisp)))
        res.append(sw.get_display_res(ndisp))
        if len(res[-1])==0:
            res[-1] = set(['800x600','640x480'])
            logging.warning('no resolutions found for display, falling back to default')
        # log resolutions
        if logging.getLogger().getEffectiveLevel() <= logging.INFO:
            logres = list(res[-1])
            logres.sort(_resolutions_sort)
            logres.reverse()
            logging.info(' resolutions: '+', '.join(logres))
    return res


def get_common_resolutions(res):
    '''return a list of common resolutions from an array of resolution-sets
    as returned by get_resolutions(). return value is sorted from high to
    low.'''
    commonres = res[0]
    for n in range(1,len(res)):
        commonres.intersection_update(res[n])
    commonres = list(commonres)
    commonres.sort(_resolutions_sort)
    commonres.reverse()
    return commonres


def _resolutions_sort(a, b):
    '''sort function for resolution strings in the form "WxH", sorts
    by number of pixels W*H.'''
    ax,ay = map(int, a.partition('x')[::2])
    bx,by = map(int, b.partition('x')[::2])
    return ax*ay - bx*by


def main():
    '''main program entry point'''
    ### option defitions
    usage = "usage: %prog [options]"
    version = ' '.join(map(str, [progname, progver]))
    parser = optparse.OptionParser(usage, version=version)
    parser.set_defaults(resolution='auto')

    parser.add_option('-v', '--verbose', action='store_const', dest='debug', const=logging.INFO,
        help='show what\'s happening')
    parser.add_option('-q', '--quiet', action='store_const', dest='debug', const=logging.ERROR,
        help='show what\'s happening')
    parser.add_option('-r', '--resolution', dest='resolution',  
        help='set resolution, or "auto" to detect')

    group = optparse.OptionGroup(parser, 'Actions',
        'Select exactly one of the following actions')
    group.add_option('-s', '--single', action='append_const', const='single', dest='actions',
        help='only enable the primary display')
    group.add_option('-c', '--clone', action='append_const', const='clone', dest='actions',
        help='clone all detected displays')
    parser.add_option_group(group)

    (options, args) = parser.parse_args()
    logging.basicConfig(level=options.debug, format='[%(levelname)s] %(message)s')
    if not options.actions: options.actions = []
    if len(options.actions) == 0:
        logging.info('no action specified, doing nothing')
    elif len(options.actions) > 2:
        parser.error('conflicting actions, please specify exactly one action: '
                     +','.join(options.actions))
        sys.exit(2)

    ### go to work
    nv = NVidiaSwitcher()
    # TODO determine displays involved
    if 'single' in options.actions:
        pass
    # determine resolution
    resolution = options.resolution
    if resolution == 'auto':
        res = get_resolutions(nv)
        commonres = get_common_resolutions(res)
        if len(commonres)==0:
            logging.critical('displays share no common resolution')
            sys.exit(1)
        resolution = commonres[0]
    # execute action
    if 'clone' in options.actions:
        nv.switch_clone(resolution)
    if 'single' in options.actions:
        nv.switch_single(resolution)


if __name__ == "__main__":
    main()

# vim:ts=4:sw=4:expandtab:
