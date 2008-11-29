##############################################################################
# metamodes.py - metamode parsing for nvidia GPUs
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

import re


class MetaModeDisplay:
    '''Display part of a MetaMode'''

    display = None
    physical = None
    virtual = None
    position = None

    def __init__(self, value=None):
        self.set(value)

    def set(self, value):
        self.display = self.physical = self.virtual = self.position = None
        if not value: return
        r = re.match(r'^\s*(\S+)\s*:\s*(.*?)\s*$', value)
        if not r: raise ValueError('malformed metamode portion: %s'%value)
        self.display, dmm = r.group(1), r.group(2)
        if dmm == 'NULL': return
        dmmparts = dmm.split()
        self.physical = map(int, dmmparts.pop(0).split('x'))
        if len(dmmparts) > 0 and dmmparts[0][0]=='@':
            self.virtual = dmmparts.pop(0)
            self.virtual = map(int, self.virtual[1:].split('x'))
        if len(dmmparts) > 0:
            r = re.match(r'^([+-]\d+)([+-]\d+)$', dmmparts.pop(0))
            if not r: raise ValueError('malformed metamode portion (bad position): %s'%value)
            self.position = [int(r.group(1)), int(r.group(2))]
        if len(dmmparts) > 0:
            raise ValueError('malformed metamode portion (too many components): %s'%value)

    def __str__(self):
        if not self.display:
            return self.__repr__()
        s = '%s: '%self.display

        if type(self.physical) == list:
            s += '%dx%d'%(self.physical[0],self.physical[1])
        elif not self.physical:
            s += 'NULL'
        else:
            s += str(self.display)

        if self.virtual:
            s += ' @%dx%d'%(self.virtual[0],self.virtual[1])
        if self.position:
            s += ' %+d%+d'%(self.position[0],self.position[1])
        return s

    def __eq__(self, other):
        # fallback to physical resolution for viewport if not set
        virtualS = self.virtual
        if not virtualS: virtualS = self.physical
        virtualO = other.virtual
        if not virtualO: virtualO = other.physical
        return self.display == other.display and self.physical == other.physical \
            and virtualS == virtualO and self.position == other.position

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return bool(self.display) and bool(self.physical)



class MetaMode:
    '''A MetaMode line'''

    id = None       # integer id of the modeline, if any
    options = {}    # options for modeline
    metamodes = []  # configuration for each display
    src = None      # source line, required for deleting a metamode

    def __init__(self, value=None):
        self.set(value)

    def set(self, value):
        self.src = value
        self.id = None
        self.options = {}
        self.metamodes = []
        if not value: return
        opts, sep, line = value.partition('::')
        if not line:
            line = opts
            opts = None
        # parse options
        if opts:
            opts = map(lambda x: x.strip(), opts.split(','))
            for opt in opts:
                key, sep, val = opt.partition('=')
                self.options[key] = val
            if 'id' in self.options:
                self.id = int(self.options['id'])
        # parse display settings
        for disp in line.split(','):
            self.metamodes.append(MetaModeDisplay(disp))

    def __str__(self):
        s = ''
        s += ', '.join(map(lambda x: '%s=%s'%(x,self.options[x]), self.options.keys()))
        s += ' :: '
        s += ', '.join(map(str, self.metamodes))
        return s

    def __eq__(self, other):
        # compare by id if int, str, or MetaMode
        if type(other) == int:
            return self.id == other
        elif type(other) == str:
            return self == MetaMode(other)
        else:
            #return self.options == other.options and self.metamodes == other.metamodes
            if len(self.metamodes) != len(other.metamodes): return False
            for m in self.metamodes:
                if not m in other.metamodes: return False
            return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return len(self.metamodes)>0


class MetaModeList(list):
    '''A list of MetaModes.'''

    def __init__(self, metamodes=None):
        list.__init__(self)
        if metamodes: 
            for m in metamodes:
                self.append(MetaMode(m))

    def find(self, el):
        '''find a MetaMode by either id or string'''
        for i in self:
            if i == el:
                return i


# a little testing
if __name__ == '__main__':
    # this is not a realistic metamode list, but it does contain a lot of
    # combinations that may appear in various configurations (and more).
    metamodesstr = [
        'source=xconfig, id=50, switchable=yes :: CRT-0: 1280x1024 @1280x1024 +1280+0, DFP-0: 1280x1024 @1280x1024 +0+0',
        'source=xconfig, id=51, switchable=yes :: CRT-0: 1024x768 @1024x768 +1024+0, DFP-0: 1024x768 @1024x768 +0+0',
        'source=xconfig, id=60, switchable=no :: CRT-0: 800x600 @800x600 -800-0, DFP-0: NULL',
        'source=xconfig, id=62, switchable=no :: DFP-0: 640x480 @640x480 +640+0, TV-0: 1024x768 @1024x768 +0+0',
        'id=63 :: DFP-9: 640x480 @640x480 +640+0, DFP-2: 123x321 @567x765 +640+0',
        '   id=64    ::  CRT-0  :      800x600    @800x600       +0+0   ',
        'id=65::CRT-1:800x600 @800x600 +0+0',
        'id=66 :: CRT-0: 10x10 @10x10 +1024+0, DFP-0: 10x10 @10x10 +0+0, TV-0: 10x10 @10x10 +0+0',
    ]
    mms = MetaModeList(metamodesstr)

    # make sure all are processed
    if len(mms) != len(metamodesstr):
        print 'ERROR: length %d != %d'%( len(mms), len(metamodestr) )

    # access all of them by id
    for i,mm in enumerate(mms):
        if mms.find(mm.id).src != mm.src:
            print 'ERROR: find by id failed for id %d' % mm.id
        if mms.find(str(mm)).src != mm.src:
            print 'ERROR: find by str failed for id %d' % mm.id
        if MetaMode(metamodesstr[i]) != mm:
            print 'ERROR: find by MetaMode failed for id %d' % mm.id

    # find variations in MetaMode strings
    for mm in [ 'CRT-0: 1024x768 @1024x768 +1024+0, DFP-0: 1024x768 @1024x768 +0+0',
                'CRT-0: 1024x768 +1024+0, DFP-0: 1024x768 +0+0',
                '  CRT-0 :    1024x768   +1024+0   ,DFP-0   :  1024x768     +0+0    ',
                'DFP-0: 1024x768 +0+0, CRT-0: 1024x768 +1024+0']:
        if not mms.find(mm) or mms.find(mm).id != 51:
            print 'ERROR: find variation by str failed: %s' % mm

    for mm in [ 'DFP-9: 640x480 @640x480 +640+0, DFP-2: 123x321 @567x765 +640+0',
                'DFP-2: 123x321 @567x765 +640+0, DFP-9: 640x480 @640x480 +640+0',
                ' DFP-2   :    123x321    @567x765  +640+0  ,  DFP-9 :    640x480    @640x480  +640+0  ']:
        if not mms.find(mm) or mms.find(mm).id != 63:
            print 'ERROR: find variation by str failed: %s' % mm

    print 'tests finished.'


# vim:ts=4:sw=4:expandtab:
