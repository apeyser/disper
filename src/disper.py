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

import os
import sys
import logging
import optparse
import shlex

from switcher import Switcher, Resolution, ResolutionSelection
from plugins import Plugins
import build

# make sure to handle SystemExit when using this class in a 3rd-party program

class Disper:

    # static information
    name = 'disper'
    version = '0.3.1'
    prefix = build.prefix
    prefix_share = build.prefix_share

    # option parsing
    argv = []
    parser = None           # option parser object
    options = None          # parsed options
    args = None             # parsed arguments

    # real work
    _switcher = None        # switcher object, see Disper.switcher()
    plugins = None          # plugins object
    log = None
    conffile = None         # last configuration file read

    def __init__(self):
        self.log = logging.getLogger('disper')
        self.log.setLevel(logging.WARNING)
        self._options_init()
        self.plugins = Plugins(self)
        #self.plugins.call('init') # can't really do here since list of plugins isn't read yet
        # add default options
        # TODO do initial parsing too so errors can be traced to config
        self.options_append(self.config_read_default())

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
            help='set resolution, e.g. "800x600", or "auto" to detect the display\'s preferred '+
                 'resolution, "max" to use the maximum resolution advertised, or "off" to disable '+
                 'the display entirely. For extend it is possible to enter a single resolution for '+
                 'all displays or a comma-separated list of resolutions (one for each display). '+
                 'Beware that many displays advertise resolutions they can not fully show, '+
                 'so "max" is not advised.')
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
                 'in %s/hooks; "all" for all plugins found; "none" for no plugins.'%(
                 os.environ.get('XDG_CONFIG_HOME', os.path.join('~', '.config', 'disper'))))
        self.add_option('', '--cycle-stages', dest='cycle_stages', default='-c:-s:-S',
            help='colon-separated list command-line arguments to cycle through; "-S:-c:-s" by default')
        self.add_option('', '--reverse-cycles', action='store_const', dest='reverse_cycles', const=True,
            help='reverse the order of the stages; to be used with --cycle')

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
        self._add_option(group, '-C', '--cycle', action='append_const', const='cycle', dest='actions',
            help='cycle through the list of cycle stages')
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


    def options_append(self, args):
        '''parses command-line options; can be called multiple times'''
        self.argv += args

    def options_parse(self, args=None):
        '''parses command-line options given; adds options to current list if set'''
        if args: self.options_append(args)
        (self.options, self.args) = self.parser.parse_args(self.argv)
        # need exactly one action
        if not self.options.actions: self.options.actions = []
        elif len(self.options.actions) > 1:
            self.parser.error('conflicting actions, please specify exactly one action: '
                         +', '.join(self.options.actions))
            raise SystemExit(2)

        if 'import' in self.options.actions or 'export' in self.options.actions:
            if self.options.resolution:
                self.log.warning('specified resolution ignored for %s'%self.options.actions[0])
            if self.options.displays:
                self.log.warning('specified displays ignored for %s'%self.options.actions[0])

        # apply defaults here to be able to detect if they were set explicitly or not
        if not self.options.direction: self.options.direction = "right"
        if not self.options.resolution: self.options.resolution = "auto"
        if not self.options.displays: self.options.displays = "auto"
        if not self.options.scaling: self.options.scaling = "default"
        if not self.options.debug: self.options.debug = logging.WARNING
        if self.options.plugins == None: self.options.plugins = "user"
        if self.options.reverse_cycles == None: self.options.reverse_cycles = False
        self.log.setLevel(self.options.debug)
        self.options.plugins = map(lambda x: x.strip(), self.options.plugins.split(','))
        if self.options.displays != 'auto':
            self.options.displays = map(lambda x: x.strip(), self.options.displays.split(','))
        if self.options.resolution not in ['auto', 'max', 'off']:
            self.options.resolution = map(lambda x: x.strip(), self.options.resolution.split(','))
        self.plugins.set_enabled(self.options.plugins)

    def config_read_default(self):
        '''Return default options from configuration files'''
        # Read old-style and XDG-style configuration files
        home = os.environ.get('HOME', '/')
        xdg_config_dirs = [os.path.join(home, '.disper')] + \
                          [os.environ.get('XDG_CONFIG_HOME', os.path.join(home, '.config', 'disper'))] + \
                          os.environ.get('XDG_CONFIG_DIRS', '/etc/xdg/disper').split(':')
        xdg_config_dirs = filter(lambda x: x and os.path.exists(x), xdg_config_dirs)
        # since later configuration files override previous ones, reverse order of reading
        # TODO allow override of action, since multiple actions would now conflict
        xdg_config_dirs = reversed(xdg_config_dirs)
        opts = ''
        for d in xdg_config_dirs:
            conffile = os.path.join(d, 'config')
            if not os.path.exists(conffile): continue
            f = open(conffile, 'r')
            opts = ''
            for l in f.readlines():
                opts += l.split('#',1)[0] + ' '
            f.close()
            # remember which configuration file was read last
            self.conffile = conffile
        return shlex.split(opts)

    def switch(self):
        '''Switch to configuration as specified in the options'''
        if len(self.options.actions) == 0:
            self.log.info('no action specified')
            # show help if no action specified
            self.parser.print_help()
            raise SystemExit(2)
        if 'single' in self.options.actions:
            self.switch_primary()
        elif 'secondary' in self.options.actions:
            self.switch_secondary()
        elif 'clone' in self.options.actions:
            self.switch_clone()
        elif 'extend' in self.options.actions:
            self.switch_extend()
        elif 'export' in self.options.actions:
            print self.export_config()
        elif 'import' in self.options.actions:
            self.import_config('\n'.join(sys.stdin))
        elif 'cycle' in self.options.actions:
            self._cycle(self.options.cycle_stages.split(':'))
        elif 'list' in self.options.actions:
            # list displays with resolutions
            displays = self.options.displays
            if displays == 'auto':
                displays = self.switcher().get_displays()
            for disp in displays:
                res = self.switcher().get_resolutions_display(disp)
                res.sort()
                print 'display %s: %s'%(disp, self.switcher().get_display_name(disp))
                print ' resolutions: '+str(res)
        else:
            self.log.critical('program error, unrecognised action: '+', '.join(self.options.actions))
            raise SystemExit(2)

    def switch_primary(self, res=None):
        '''Only enable primary display.
           @param res resolution to use; or 'auto' for default or None for option'''
        if self.options.displays and self.options.displays != 'auto':
            return self.switch_single(self.options.displays[0])
        else:
            return self.switch_single(self.switcher().get_primary_display())

    def switch_secondary(self, res=None):
        '''Only enable secondary display.
           @param res resolution to use; or 'auto' for default or None for option'''
        if self.options.displays and self.options.displays != 'auto':
            if len(self.options.displays)>=2:
                return self.switch_single(self.options.displays[1])
            else:
                self.log.critical('No secondary display found, falling back to primary.')
                return self.switch_single(self.options.displays[0])
        else:
            primary = self.switcher().get_primary_display()
            try:
                display = [x for x in self.switcher().get_displays() if x != primary][0]
            except IndexError:
                self.log.critical('No secondary display found, falling back to primary.')
                return self.switch_single(primary, res)
            return self.switch_single(display, res)

    def switch_single(self, display=None, res=None):
        '''Only enable one display.
           @param display display to enable; or 'auto' for primary or None for option
           @param res resolution to use; or 'auto' for default or None for option'''
        if not display: display = self.options.displays
        if display == 'auto':
            display = self.switcher().get_primary_display()
        elif isinstance(display, list) and len(display)>1:
            self.log.warning('single output requested but multiple specified; using first one')
            display = display[0]
        if display: display = [display]
        return self.switch_clone(display, res)

    def switch_clone(self, displays=None, res=None):
        '''Clone displays.
           @param displays list of displays; or 'auto' for default or None for option
           @param res resolution; or 'auto' for default, 'max' for max, 'off' to disable
                  the display, 'none' or None for option'''
        # figure out displays
        if not displays: displays = self.options.displays
        if displays == 'auto':
            displays = self.switcher().get_displays()
            self.log.info('auto-detected displays: '+', '.join(displays))
        else:
            self.log.info('using specified displays: '+', '.join(displays))
        # figure out resolutions
        if not res:
            res = self.options.resolution
            if type(res)==list or type(res)==tuple:
                if len(res) != 1: raise TypeError('need single resolution for clone')
                res = res[0]
        if res in ['auto', 'max']:
            r = self.switcher().get_resolutions(displays).common()
            if len(r)==0:
                self.log.critical('displays share no common resolution')
                raise SystemExit(1)
            if res == 'max': # ignore any preferred resolution
                for s in r: s.weight = 0
            res = sorted(r)[-1]
        else:
            res = Resolution(res)
        # and switch
        result = self.switcher().switch_clone(displays, res)
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
            displays = self.switcher().get_displays()
            self.log.info('auto-detected displays: '+', '.join(displays))
        else:
            self.log.info('using specified displays: '+', '.join(displays))
        # figure out resolutions
        if not ress: ress = self.options.resolution
        if ress == 'max':     # max resolution for each
            # override auto-detection weights and get highest resolution
            ress = self.switcher().get_resolutions(displays)
            for rl in ress.values():
                for r in rl: r.weight = 0
            ress = ress.select()
            self.log.info('maximum resolutions for displays: '+str(ress))
        elif ress == 'auto':  # use preferred resolution for each
            ress = self.switcher().get_resolutions(displays).select()
            self.log.info('preferred resolutions for displays: '+str(ress))
        else:                       # list of resolutions specified
            ress = ResolutionSelection(ress, displays)
            if len(ress)==1:
                ress = ress * len(displays)
            elif len(ress) != len(displays):
                self.log.critical('resolution: must specify either "auto", "max", a single value, or one for each display')
                raise SystemExit(2)
            self.log.info('selected resolutions for displays: '+str(ress))
        # figure out direction
        if not direction: direction = self.options.direction
        # and switch
        result = self.switcher().switch_extend(displays, direction, ress)
        self.plugins.set_layout_extend(displays, direction, ress)
        self.plugins.call('switch')
        return result

    def export_config(self):
        return self.switcher().export_config()

    def import_config(self, data):
        result = self.switcher().import_config(data)
        self.plugins.call('switch')
        return result

    def _cycle(self, stages):
        # read last state
        stage = 0
        disperconf = None
        # TODO use X root window hint instead of file (which doesn't adhere to XDG)
        if self.conffile:
            disperconf = os.path.dirname(self.conffile)
        else:
            home = os.environ.get('HOME', '/')
            disperconf = os.environ.get('XDG_CONFIG_HOME', os.path.join(home, '.config', 'disper'))
        statefile = os.path.join(disperconf, 'last_cycle_stage')
        self.log.debug('Cycle state file: '+statefile)
        if os.path.exists(statefile):
            f = open(statefile, 'r')
            stage = int(f.readline())
            f.close()
        # apply next
        if self.options.reverse_cycles:
            stage -= 1
            if stage < 0: stage = len(stages) - 1
        else:
            stage += 1
            if stage >= len(stages): stage = 0
        self.argv = filter(lambda x: x!='-C' and x!='--cycle', self.argv)
        self.options_parse(shlex.split(stages[stage]))
        try:
            self.switch()
        finally:
            # write new state to file; do it here to make sure that a
            # failing configuration doesn't block the cycling
            if not os.path.exists(disperconf):
                self.log.info('Creating disper configuration directory for statefile: '+disperconf)
                os.mkdir(disperconf)
            f = open(statefile, 'w')
            f.write(str(stage)+'\n')
            f.close()

    def switcher(self):
        '''Return switcher object (singleton).
        This is implemented as a method, so that it can be created only when
        needed to avoid errors when displaying help.'''
        if not self._switcher:
            self._switcher = Switcher()
        return self._switcher


def main():
    disper = Disper()
    disper.options_parse(sys.argv[1:])
    disper.switch()

if __name__ == "__main__":
    # Python 2.3 doesn't support arguments to basicConfig()
    try: logging.basicConfig(format='%(message)s')
    except: logging.basicConfig()
    main()

# vim:ts=4:sw=4:expandtab:
