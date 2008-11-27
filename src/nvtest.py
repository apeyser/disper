#!/usr/bin/env python

import re
import xrandr
import nvidia

def main():
	nv = nvidia.NVidiaControl()
	screen = nvidia.Screen(nv.xscreen)

	displays = nv.probe_displays(screen)
	res = "1024x768"

	# get resolutions for all displays
	# displays must be associated for that
	nv.set_screen_associated_displays(screen, displays)

	# clone all displays. 
	metamode = ', '.join(map(lambda d: '%s: %s +0+0'%(d,res), displays))
	nv.add_screen_metamode(screen, metamode)

	# find the id of the metamode
	metamodes = nv.get_metamodes(screen)
	mmid = find_metamode_clone(metamodes, res, displays)

	# now use xrandr to switch
	xrandr_switch(res, mmid)


def find_metamode_clone(metamodes, res, displays):
	'''find the id of an existing clone metamode for a specific resolution'''
	for mm in metamodes:
		r = re.match(r'\s*id=(\d+).*::\s*(.*)$', mm)
		if not r: continue
		id = r.group(1)
		found = True
		for i,dc in enumerate(r.group(2).split(',')):
			# Every display must have real and virtual resolution
			# requested with an origin at (0,0) - that's clone.
			# When metamodes contain more entries than specified
			# monitors, require them to be disabled (NULL).
			r = re.match(r'^\s*([^:]*)\s*:\s*(.*?)\s*$', dc)
			if not r:
				found = False
				continue
			disp, mm = r.group(1), r.group(2)
			if disp in displays:
				r = re.match('^\s*'+res+'(\s+@'+res+')?\s+\+0\+0\s*$', mm)
				if not r: found = False
			else:
				r = re.match('^\s*NULL\s*$', mm)
				if not r: found = False
		if found: return int(id)
	return -1


def xrandr_switch(res, mmid):
	'''switch to the specified MetaMode id'''
	screen = xrandr.get_current_screen()
	sizeidx = None
	w,h = res.split('x')
	for i,s in enumerate(screen.get_available_sizes()):
		if int(s.width) == int(w) and int(s.height) == int(h):
			sizeidx = i
	if sizeidx == None or sizeidx == -1:
		raise Exception( 'could not set display mode: resolution not found (this is a bug)' )
	screen.set_size_index(sizeidx)
	screen.set_refresh_rate(mmid)
	screen.apply_config()

if __name__ == "__main__":
	main()

