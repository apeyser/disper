##############################################################################
# resolutions.py - managing collections of resolutions
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


class Resolution:
    '''a single resolution with a width, height, and a sort weight.
    Resolutions can be initialised from a string or a list and can be sorted.'''
    
    width = None    # horizontal size of resolution
    height = None   # vertical size of resolution
    weight = 0      # how 'important' this resolution is for sorting
	
    def __init__(self, val=None, weight=None):
        self.set(val, weight)

    def set(self, val, weight=None):
        '''set resolution. Value can be either None, a string in the form
        "WIDTHxHEIGHT", another Resolution instance, or a list [width,height].
        when weight is not None, it will be set.'''
        self.width = self.height = None
        if weight != None: self.weight = weight
        if isinstance(val, Resolution):
            self.height = val.height
            self.width = val.width
            self.weight = val.weight
        elif val == None:
            self.width = self.height = None
        elif type(val) == str:
            self.width,self.height = map(int, val.partition('x')[::2])
        else:
            self.width,self.height = val

    def size(self):
        return self.width, self.height

    def __str__(self):
        return '%dx%d'%(self.width,self.height)

    def __eq__(self, other):
        if not isinstance(other, Resolution):
            try: other = Resolution(other)
            except: return False
        return (self.width == other.width) and (self.height == other.height)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __cmp__(self, other):
        # sort order: by number of pixels, but native resolutions at the end
        if not isinstance(other, Resolution):
            other = Resolution(other)
        if self.weight != other.weight: return self.weight - other.weight
        return self.width*self.height - other.width*other.height

    def __hash__(self):
        return hash(self.__str__())


class ResolutionList(list):
    '''a list of resolutions'''

    def __init__(self, val=None):
        self.set(val)

    def set(self, val):
        self[:] = []
        if val == None: return
        if type(val) == str:
            val = val.split(',')
        for v in val:
            self.append(Resolution(v))

    def __str__(self):
        return ', '.join(map(str, self))

    def __cmp__(self, other):
        if not isinstance(other, ResolutionList):
            other = ResolutionList(other)
        return cmp(list(self), list(other))


class ResolutionSelection(dict):
    '''a hash containing one resolution for each display'''

    def __init__(self, sress=None, displays=None):
        '''create new ResolutionSelection, optionally from a string of
        resolutions in the form "800x600, 240x340", one resolution for
        each display. Alternatively if sress contains only one
        resolution, this is used for each display.'''
        self.set(sress, displays)

    def set(self, sress, displays=None):
        self.clear()
        if not sress: return
        if isinstance(sress, ResolutionSelection):
            # copy from other object
            for i in sress: self.append(i)
        elif type(sress)==str:
            # parse from string
            sress = sress.split(',')
            if len(sress) == 1:
                sress = sress * len(displays)
            elif len(sress) != len(displays):
                raise ValueError('number of resolutions must be equal to number of displays')
            for i,sr in enumerate(sress):
                self[displays[i]] = Resolution(sr)
        else:
            raise ValueError('unrecognised resolution selection')

    def __str__(self):
        s = []
        for disp,r in self.iteritems():
            s.append('%s: %s'%(disp, r))
        return ', '.join(s)


class ResolutionCollection(dict):
    '''a hash containing a list of resolutions for each display'''

    def __str__(self):
        s = []
        for disp,rl in self.iteritems():
            s.append('%s: %s'%(disp, rl))
        return '\n'.join(s)

    def common(self):
        '''return ResolutionList with only resolutions common to all displays.
        The weight of each resolution is the sum of that of each display.'''
        if len(self) == 0: return ResolutionList()
        common = None
        for disp,rl in self.iteritems():
            if not common:
                common = ResolutionList(rl)
                continue
            delitems = ResolutionList()
            for c in common:
                if c in rl:
                    c.weight += rl[rl.index(c)].weight
                else:
                    delitems.append(c)
            for d in delitems: common.remove(d)
        return common

    def sort(self):
        '''sort all contained resolution lists'''
        for disp,rl in self.iteritems():
            rl.sort()

    def reverse(self):
        '''reverse all contained resolution lists'''
        for disp,rl in self.iteritems():
            rl.reverse()

    def select(self, choose=lambda disp,rl: sorted(rl)[-1]):
        '''return a dict containing the topmost resolution for each display.
        This is useful to get an actual resolution for each display after having
        sorted each contained ResolutionList with the best resolution at the
        end. Or if another selection criterion is wanted, it can be specified.'''
        r = ResolutionSelection()
        for disp,rl in self.iteritems():
            r[disp] = choose(disp, rl)
        return r


# some testing
if __name__ == '__main__':
    r = Resolution('800x600')
    if r != Resolution('800x600'):
        print 'ERROR: resolution string init, resolution compare: %s'%r
    if r != [800, 600]:
        print 'ERROR: resolution string init, list compare: %s'%r
    if r != '   800    x 600  ':
        print 'ERROR: resolution string init, string compare: %s'%r

    if not Resolution([1024, 768]) > r:
        print 'ERROR: resolution compare'
    if Resolution([640,480], 1) <= r:
        print 'ERROR: sort order 1 vs 0'
    if Resolution([640,480], -5) >= r:
        print 'ERROR: sort order -5 vs 0'

    rl = ResolutionList(' 640x480,    1024   x   768 , 800x600, 200x300  ')
    rl2 = ResolutionList(['640x480', '1024x768', '800x600', '200x300'])
    rl3 = ResolutionList([[640,480], [1024,768], [800,600], [200,300]])
    if rl != rl2:
        print 'ERROR: resolutionlist string vs. list of strings'
    if rl != rl3:
        print 'ERROR: resolutionlist string vs. list of lists'
    if '800x600' not in rl:
        print 'ERROR: cannot find string resolution in list'
    if [800,600] not in rl:
        print 'ERROR: cannot find list resolution in list'

    rl.sort()
    if rl != '200x300, 640x480, 800x600, 1024x768':
        print 'ERROR: resolution list sort: %s'%rl

    rc = ResolutionCollection()
    rl1 = ResolutionList('640x480, 200x300, 600x800, 1024x800, 400x800, 400x300')
    rl2 = ResolutionList('800x600, 1000x800, 200x300, 400x300, 500x300')
    rc['display1'] = rl1
    rc['display2'] = rl2

    if rc.common() != '200x300, 400x300':
        print 'ERROR: resolution collection common'
    if rc.select() != {'display1': Resolution('1024x800'), 'display2': Resolution('1000x800')}:
        print 'ERROR: resolution collection select'

    rcsorted = ResolutionCollection()
    rcsorted['display1'] = sorted(rl1)
    rcsorted['display2'] = sorted(rl2)
    if rc == rcsorted:
        print 'ERROR: resolution collections should not be equal before sorting'
    rc.sort()
    if rc != rcsorted:
        print 'ERROR: inplace sorting failed'

    print 'all tests done.'

# vim:ts=4:sw=4:expandtab:
