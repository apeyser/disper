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

import switcher

# program name and version
progname = 'disper'
progver = '0.1.3'


def get_resolutions_display(sw, disp):
    '''return a set of resolution for the specified display'''
    r = sw.get_display_supported_res(disp)
    if len(r)==0:
        r = set(['800x600','640x480'])
        logging.warning('no resolutions found for display %s, falling back to default'%disp)
    return r

def get_resolutions(sw, displays = []):
    '''return an array of resolution-sets for each display connected'''
    if len(displays) == 0:
        displays = sw.get_displays()
    res = []
    for disp in displays:
        res.append(get_resolutions_display(sw, disp))
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


def do_main():
    '''main program entry point'''
    ### option defitions
    usage = "usage: %prog [options] (-l|-s|-c|-e|-p|-i)"
    version = ' '.join(map(str, [progname, progver]))
    parser = optparse.OptionParser(usage=usage, version=version)

    parser.add_option('-v', '--verbose', action='store_const', dest='debug', const=logging.INFO,
        help='show what\'s happening')
    parser.add_option('-q', '--quiet', action='store_const', dest='debug', const=logging.ERROR,
        help='be quiet and only show errors')
    parser.add_option('-r', '--resolution', dest='resolution',  
        help='set resolution, e.g. "800x600", or "auto" to detect the highest common '+
             'resolution. For extend it is also possible to enter a comma-separated list '+
             'of resolutions (one for each display), or "max" to use the maximum '+
             'resolution for each device.')
    parser.add_option('-d', '--displays', dest='displays',
        help='comma-separated list of displays to operate on, or "auto" to detect')
    parser.add_option('-t', '--direction', dest='direction',
        choices=['left','right','top','bottom'],
        help='where to extend displays: "left", "right", "top", or "bottom"')

    group = optparse.OptionGroup(parser, 'Actions',
        'Select exactly one of the following actions')
    group.add_option('-l', '--list', action='append_const', const='list', dest='actions',
        help='list the attached displays')
    group.add_option('-s', '--single', action='append_const', const='single', dest='actions',
        help='only enable the primary display')
    group.add_option('-c', '--clone', action='append_const', const='clone', dest='actions',
        help='clone displays')
    group.add_option('-e', '--extend', action='append_const', const='extend', dest='actions',
        help='extend displays')
    group.add_option('-p', '--export', action='append_const', const='export', dest='actions',
        help='export current settings to standard output')
    group.add_option('-i', '--import', action='append_const', const='import', dest='actions',
        help='import current settings from standard input')
    parser.add_option_group(group)

    (options, args) = parser.parse_args()
    # need exactly one action
    if not options.actions: options.actions = []
    if len(options.actions) == 0:
        logging.info('no action specified')
        # show help if no action specified
        parser.print_help()
        sys.exit(0)
    elif len(options.actions) > 1:
        parser.error('conflicting actions, please specify exactly one action: '
                     +', '.join(options.actions))
        sys.exit(2)

    if 'import' in options.actions or 'export' in options.actions:
        if options.resolution:
            logging.warning('specified resolution ignored for %s'%options.actions[0])
        if options.displays:
            logging.warning('specified displays ignored for %s'%options.actions[0])

    # apply defaults here to be able to detect if they were set explicitly or not
    if not options.direction: options.direction = "right"
    if not options.resolution: options.resolution = "auto"
    if not options.displays: options.displays = "auto"
    if not options.debug: options.debug = logging.WARNING
    logging.getLogger().setLevel(options.debug)

    ### autodetect and apply options
    sw = switcher.Switcher()

    # determine displays involved
    if 'single' in options.actions:
        if options.displays == 'auto':
            options.displays = sw.get_primary_display()
        elif options.displays != [sw.get_primary_display()]:
            logging.warning('cloning specified displays instead of selecting primary display only')
        options.actions = ['clone']
    if options.displays == 'auto':
        options.displays = sw.get_displays()
        logging.info('auto-detected displays: '+', '.join(options.displays))
    else:
        options.displays = map(lambda x: x.strip(), options.displays.split(','))
        logging.info('using specified displays: '+', '.join(options.displays))

    ### execute action
    if 'list' in options.actions:
        # list displays with resolutions
        for disp in options.displays:
            res = get_resolutions_display(sw, disp)
            logres = list(res)
            logres.sort(_resolutions_sort)
            logres.reverse()
            print 'display %s: %s'%(disp, sw.get_display_name(disp))
            print ' resolutions: '+', '.join(logres)

    elif 'clone' in options.actions:
        # determine resolution
        resolution = options.resolution
        if resolution == 'auto':
            res = get_resolutions(sw, options.displays)
            commonres = get_common_resolutions(res)
            if len(commonres)==0:
                logging.critical('displays share no common resolution')
                sys.exit(1)
            resolution = commonres[0]
        # and switch
        sw.switch_clone(options.displays, resolution)

    elif 'extend' in options.actions:
        # determine resolutions
        resolution = options.resolution
        if resolution == 'max':     # max resolution for each
            ress = get_resolutions(sw, options.displays)
            # TODO find optimal resolution for each display, might not be maximum
            ress = map(lambda x: get_common_resolutions([x])[0], ress)
            logging.info('maximum resolutions for displays: '+', '.join(ress))
        elif resolution == 'auto':  # use preferred resolution for each
            ress = []
            allress = get_resolutions(sw, options.displays)
            for i,d in enumerate(options.displays):
                r = sw.get_display_preferred_res(d)
                if not r:
                    r = get_common_resolutions([allress[i]])[0]
                ress.append(r)
            logging.info('preferred resolutions for displays: '+', '.join(ress))
        else:                       # list of resolutions specified
            ress = map(lambda x: x.strip(), resolution.split(','))
            if len(ress)==1:
                ress = ress * len(options.displays)
            elif len(ress) != len(options.displays):
                logging.critical('resolution: must specify either "auto", "max", a single value, or one for each display')
                sys.exit(2)
            logging.info('selected resolutions for displays: '+', '.join(ress))
        # and switch
        sw.switch_extend(options.displays, options.direction, ress)
        
    elif 'export' in options.actions:
        print sw.export_config()

    elif 'import' in options.actions:
        sw.import_config('\n'.join(sys.stdin))

    else:
        logging.critical('program error, unrecognised action: '+', '.join(options.actions))
        sys.exit(2)


def main():
    logging.basicConfig(level=logging.WARNING, format='%(message)s')

    try:
        do_main()
    except Exception,e:
        logging.error(str(e))
        raise # for debugging
        sys.exit(1)

if __name__ == "__main__":
    main()

# vim:ts=4:sw=4:expandtab:
