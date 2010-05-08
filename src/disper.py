#!/usr/bin/env python
###############################################################################
# disper.py - main disper
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

import sys
import logging
import optparse

from switcher import Switcher
from plugins import Plugins


# make sure to handle SystemExit when using this class in a 3rd-party program

class Disper:

    # program name and version
    name = 'disper'
    version = '0.2.3'

    # option parsing
    argv = []
    parser = None           # option parser object
    options = None          # parsed options
    args = None             # parsed arguments

    # real work
    switcher = None         # switcher object
    plugins = None          # plugins object
    

    def __init__(self):
        self._options_init()
        self.plugins = Plugins(self)
        #self.plugins.call('init') # can't really do here since list of plugins isn't read yet
        self.switcher = Switcher()

    def _options_init(self):
        '''initialize default command-line options'''
        usage = "usage: %prog [options] (-l|-s|-c|-e|-p|-i)"
        version = ' '.join(map(str, [self.name, self.version]))
        self.parser = optparse.OptionParser(usage=usage, version=version)

        self.add_option('-v', '--verbose', action='store_const', dest='debug', const=logging.INFO,
            help='show what\'s happening')
        self.add_option('-q', '--quiet', action='store_const', dest='debug', const=logging.ERROR,
            help='be quiet and only show errors')
        self.add_option('-r', '--resolution', dest='resolution',  
            help='set resolution, e.g. "800x600", or "auto" to detect the highest common '+
                 'resolution. For extend it is possible to enter a single resolution for '+
                 'all displays, or a comma-separated list of resolutions (one for each '+
                 'display), or "max" to use the maximum resolution for each device. Beware '+
                 'that many displays advertise resolutions they can not fully show, so '+
                 '"max" is not advised.')
        self.add_option('-d', '--displays', dest='displays',
            help='comma-separated list of displays to operate on, or "auto" to detect; '+
                 'the first is the primary display.')
        self.add_option('-t', '--direction', dest='direction',
            choices=['left','right','top','bottom'],
            help='where to extend displays: "left", "right", "top", or "bottom"')
        self.add_option('', '--scaling', dest='scaling',
            choices=['default','native','scaled','centered','aspect-scaled'],
            help='flat-panel scaling mode: "default", "native", "scaled", "centered", or "aspect-scaled"')
        self.add_option('', '--plugins', dest='plugins',
            help='comma-separated list of plugins to enable. Special names: "user" for all user plugins '+
                 'in ~/.disper/hooks; "all" for all plugins found')

        group = optparse.OptionGroup(self.parser, 'Actions',
            'Select exactly one of the following actions')
        self._add_option(group, '-l', '--list', action='append_const', const='list', dest='actions',
            help='list the attached displays')
        self._add_option(group, '-s', '--single', action='append_const', const='single', dest='actions',
            help='only enable the primary display')
        self._add_option(group, '-S', '--secondary', action='append_const', const='secondary', dest='actions',
            help='only enable the secondary display')
        self._add_option(group, '-c', '--clone', action='append_const', const='clone', dest='actions',
            help='clone displays')
        self._add_option(group, '-e', '--extend', action='append_const', const='extend', dest='actions',
            help='extend displays')
        self._add_option(group, '-p', '--export', action='append_const', const='export', dest='actions',
            help='export current settings to standard output')
        self._add_option(group, '-i', '--import', action='append_const', const='import', dest='actions',
            help='import current settings from standard input')
        self.parser.add_option_group(group)


    def add_option(self, *args, **kwargs):
        '''adds an option to the parser. Implements append_const for Python<2.5 too'''
        return self._add_option(self.parser, *args, **kwargs)

    def _add_option(self, obj, *args, **kwargs):
        '''portable optarg add_option function that implements the append_const
        action for Python versions below 2.5; has an extra first argument as
        the object on which add_option should be called.'''
        if sys.hexversion < 0x020500f0 and 'action' in kwargs and \
                kwargs['action'] == 'append_const':
            # after: http://permalink.gmane.org/gmane.comp.python.optik.user/284
            def append_const_cb(const):
                def cb(opt, opt_str, value, parser):
                    if not getattr(parser.values, opt.dest):
                        setattr(parser.values, opt.dest, list())
                    getattr(parser.values, opt.dest).append(const)
                return cb
            kwargs['action'] = 'callback'
            kwargs['callback'] = append_const_cb(kwargs['const'])
            del kwargs['const']
        return obj.add_option(*args, **kwargs)


    def options_parse(self, args):
        '''parses the command-line options'''
        self.argv = args
        (self.options, self.args) = self.parser.parse_args(args)
        # need exactly one action
        if not self.options.actions: self.options.actions = []
        if len(self.options.actions) == 0:
            logging.info('no action specified')
            # show help if no action specified
            self.parser.print_help()
            raise SystemExit(2)
        elif len(self.options.actions) > 1:
            parser.error('conflicting actions, please specify exactly one action: '
                         +', '.join(self.options.actions))
            raise SystemExit(2)

        if 'import' in self.options.actions or 'export' in self.options.actions:
            if self.options.resolution:
                logging.warning('specified resolution ignored for %s'%self.options.actions[0])
            if self.options.displays:
                logging.warning('specified displays ignored for %s'%self.options.actions[0])

        # apply defaults here to be able to detect if they were set explicitly or not
        if not self.options.direction: self.options.direction = "right"
        if not self.options.resolution: self.options.resolution = "auto"
        if not self.options.displays: self.options.displays = "auto"
        if not self.options.scaling: self.options.scaling = "default"
        if not self.options.debug: self.options.debug = logging.WARNING
        if self.options.plugins == None: self.options.plugins = "user"
        logging.getLogger().setLevel(self.options.debug)
        self.options.plugins = map(lambda x: x.strip(), self.options.plugins.split(','))
        if self.options.displays != 'auto':
            self.options.displays = map(lambda x: x.strip(), self.options.displays.split(','))
        if self.options.resolution not in ['auto', 'max']:
            self.options.resolution = map(lambda x: x.strip(), self.options.resolution.split(','))
        self.plugins.set_enabled(self.options.plugins)

    def switch(self):
        '''Switch to configuration as specified in the options'''
        if 'single' in self.options.actions:
            if self.options.displays != 'auto':
                logging.warning('specified displays ignored for single')
            self.switch_primary()
        elif 'secondary' in self.options.actions:
            if self.options.displays != 'auto':
                logging.warning('specified displays ignored for secondary')
            self.switch_secondary()
        elif 'clone' in self.options.actions:
            self.switch_clone()
        elif 'extend' in self.options.actions:
            self.switch_extend()
        elif 'export' in self.options.actions:
            print self.export_config()
        elif 'import' in self.options.actions:
            self.import_config('\n'.join(sys.stdin))
        elif 'list' in self.options.actions:
            # list displays with resolutions
            displays = self.options.displays
            if displays == 'auto':
                displays = self.switcher.get_displays()
            for disp in displays:
                res = self.switcher.get_resolutions_display(disp)
                res.sort()
                print 'display %s: %s'%(disp, self.switcher.get_display_name(disp))
                print ' resolutions: '+str(res)
        else:
            logging.critical('program error, unrecognised action: '+', '.join(self.options.actions))
            raise SystemExit(2)

    def switch_primary(self, res=None):
        '''Only enable primary display.
           @param res resolution to use; or 'auto' for default or None for option'''
        return self.switch_single(self.switcher.get_primary_display())

    def switch_secondary(self, res=None):
        '''Only enable secondary display.
           @param res resolution to use; or 'auto' for default or None for option'''
        primary = self.switcher.get_primary_display()
        try:
            display = [x for x in self.switcher.get_displays() if x != primary][0]
        except IndexError:
            logging.critical('No secondary display found, falling back to primary.')
            return self.switch_single(primary, res)
        return self.switch_single(display, res)

    def switch_single(self, display=None, res=None):
        '''Only enable one display.
           @param display display to enable; or 'auto' for primary or None for option
           @param res resolution to use; or 'auto' for default or None for option'''
        if not display: display = self.options.displays
        if display == 'auto':
            display = self.switcher.get_primary_display()
        elif isinstance(display, list) and len(display)>1:
            logging.warning('single output requested but multiple specified; using first one')
            display = display[0]
        if res: res = [res]
        if display: display = [display]
        return self.switch_clone(display, res)

    def switch_clone(self, displays=None, res=None):
        '''Clone displays.
           @param displays list of displays; or 'auto' for default or None for option
           @param res resolution; or 'auto' for default or None to for option'''
        # figure out displays
        if not displays: displays = self.options.displays
        if displays == 'auto':
            displays = self.switcher.get_displays()
            logging.info('auto-detected displays: '+', '.join(displays))
        else:
            logging.info('using specified displays: '+', '.join(displays))
        # figure out resolutions
        if not res: res = self.options.resolution
        if res == 'auto':
            r = self.switcher.get_resolutions(displays).common()
            if len(r)==0:
                logging.critical('displays share no common resolution')
                raise SystemExit(1)
            res = sorted(r)[-1]
        else:
            res = switcher.Resolution(resolution)
        # and switch
        result = self.switcher.switch_clone(displays, res)
        self.plugins.set_layout_clone(displays, res)
        self.plugins.call('switch')
        return result

    def switch_extend(self, displays=None, direction=None, ress=None):
        '''Extend displays.
           @param displays list of displays; or 'auto for default or None for option
           @param direction direction to extend; or None for option
           @param ress list of resolutions; or 'auto' for default or 'max' for max or None for option'''
        # figure out displays
        if not displays: displays = self.options.displays
        if displays == 'auto':
            displays = self.switcher.get_displays()
            logging.info('auto-detected displays: '+', '.join(displays))
        else:
            logging.info('using specified displays: '+', '.join(displays))
        # figure out resolutions
        if not ress: ress = self.options.resolution
        if ress == 'max':     # max resolution for each
            # override auto-detection weights and get highest resolution
            ress = self.switcher.get_resolutions(displays)
            for rl in ress.values():
                for r in rl: r.weight = 0
            ress = ress.select()
            logging.info('maximum resolutions for displays: '+str(ress))
        elif ress == 'auto':  # use preferred resolution for each
            ress = self.switcher.get_resolutions(displays).select()
            logging.info('preferred resolutions for displays: '+str(ress))
        else:                       # list of resolutions specified
            ress = self.switcher.ResolutionSelection(ress, displays)
            if len(ress)==1:
                ress = ress * len(displays)
            elif len(ress) != len(displays):
                logging.critical('resolution: must specify either "auto", "max", a single value, or one for each display')
                raise SystemExit(2)
            logging.info('selected resolutions for displays: '+str(ress))
        # figure out direction
        if not direction: direction = self.options.direction
        # and switch
        result = self.switcher.switch_extend(displays, direction, ress)
        self.plugins.set_layout_extend(displays, direction, ress)
        self.plugins.call('switch')
        return result

    def export_config(self):
        return self.switcher.export_config()

    def import_config(self, data):
        result = self.switcher.import_config(data)
        self.plugins.call('switch')
        return result

def main():
    disper = Disper()
    disper.options_parse(sys.argv[1:])
    disper.switch()

if __name__ == "__main__":
    # Python 2.3 doesn't support arguments to basicConfig()
    try: logging.basicConfig(format='%(message)s')
    except: logging.basicConfig()
    logging.getLogger().setLevel(logging.WARNING)
    main()

# vim:ts=4:sw=4:expandtab: