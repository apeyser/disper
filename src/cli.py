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
             'resolution. For extend it is possible to enter a single resolution for '+
             'all displays, or a comma-separated list of resolutions (one for each '+
             'display), or "max" to use the maximum resolution for each device. Beware '+
             'that many displays advertise resolutions they can not fully show, so '+
             '"max" is not advised.')
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
            res = sw.get_resolutions_display(disp)
            res.sort()
            print 'display %s: %s'%(disp, sw.get_display_name(disp))
            print ' resolutions: '+str(res)

    elif 'clone' in options.actions:
        # determine resolution
        resolution = options.resolution
        if resolution == 'auto':
            res = sw.get_resolutions(options.displays).common()
            if len(res)==0:
                logging.critical('displays share no common resolution')
                sys.exit(1)
            resolution = sorted(res)[-1]
        else:
            resolution = switcher.Resolution(resolution)
        # and switch
        sw.switch_clone(options.displays, resolution)

    elif 'extend' in options.actions:
        # TODO rework this to code reorganisation
        # determine resolutions
        resolution = options.resolution
        if resolution == 'max':     # max resolution for each
            # override auto-detection weights and get highest resolution
            ress = sw.get_resolutions(options.displays)
            for rl in ress.values():
                for r in rl: r.weight = 0
            ress = ress.select()
            logging.info('maximum resolutions for displays: '+str(ress))
        elif resolution == 'auto':  # use preferred resolution for each
            ress = sw.get_resolutions(options.displays).select()
            logging.info('preferred resolutions for displays: '+str(ress))
        else:                       # list of resolutions specified
            ress = switcher.ResolutionSelection(resolution, options.displays)
            if len(ress)==1:
                ress = ress * len(options.displays)
            elif len(ress) != len(options.displays):
                logging.critical('resolution: must specify either "auto", "max", a single value, or one for each display')
                sys.exit(2)
            logging.info('selected resolutions for displays: '+str(ress))
        # and switch
        sw.switch_extend(options.direction, ress)
        
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
