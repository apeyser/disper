#!/usr/bin/env python

import re
import xrandr
import nvidia


def main():
	nv = nvidia.NVidiaControl()
	screen = nvidia.Screen(nv.xscreen)

	newdisplays = nv.probe_displays(screen)
	res = "1024x768"
	#res = detect_resolutions(nv, screen, newdisplays)

	print 'probed displays:',', '.join(newdisplays)
	print 'probed resolution:',res

	# associate displays; associate both the original and the new
	# displays so that we can switch to the new mode and then delete
	# the old one when required; all displays mentioned in the metamode
	# must be associated for cleanup_metamodes() to work.
	olddisplays = nv.get_screen_associated_displays(screen)
	assocdisplays = set(newdisplays).union(set(olddisplays))
	nv.set_screen_associated_displays(screen, assocdisplays)

	# clone all displays. 
	metamode = ', '.join(map(lambda d: '%s: %s +0+0'%(d,res), newdisplays))
	print 'creating metamode:',metamode
	nv.add_screen_metamode(screen, metamode)

	# find the id of the metamode (can't get string operation to work which
	# returns an id after creation; also don't think that add_screen_metamode
	# would return the id if the metamode already exists)
	metamodes = nv.get_metamodes(screen)
	mmid = find_metamode_clone(metamodes, res, newdisplays)
	print 'switching to metamode:',mmid

	# now use xrandr to switch
	xrandr_switch(res, mmid)

	# cleanup incompatible metamodes
	cleanup_metamodes(nv, screen, newdisplays)
	# and dissociate old screen
	nv.set_screen_associated_displays(screen, newdisplays)


def find_metamode_clone(metamodes, res, displays):
	'''find the id of an existing clone metamode for a specific resolution'''
	foundid = -1
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
		if found:
			if foundid > 0:
				raise Exception('Multiple matching modes found')
			foundid = int(id)
	return foundid


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


def detect_resolutions(nv, screen, displays):
	'''return resolutions common to all displays.'''
	resolutions = None
	olddisplays = nv.get_screen_associated_displays(screen)
	assocdisplays = set(olddisplays).union(set(displays))
	nv.set_screen_associated_displays(screen, displays)
	# a modeline is needed or X will crash
	metamode = ', '.join(map(lambda d: 'nvidia-auto-select',displays))
	tmpid = nv.add_screen_metamode(screen, metamode)
	for d in displays:
		nv.build_modepool(screen, d)
		curres = set()
		for m in nv.get_display_modelines(screen, d):
			r = re.search(r'::\s*"(\d+x\d+)"', m)
			if not r: continue
			curres.add(r.group(1))
		if not resolutions:
			resolutions = curres
		else:
			resolutions.intersection_update(curres)
	# sort by width
	resolutions = list(resolutions)
	resolutions.sort(lambda a,b: int(a.partition('x')[0])-int(b.partition('x')[0]))
	print 'common resolutions:',', '.join(resolutions)
	# revert screen association and remove temporary metamode
	if tmpid > 0:
		nv.delete_screen_metamode(screen, tmpid)
	nv.set_screen_associated_displays(screen, olddisplays)
	# we want the highest common resolution
	return resolutions[-1]


def cleanup_metamodes(nv, screen, displays):
	'''cleanup metamodes referencing displays not mentioned'''
	metamodes = nv.get_metamodes(screen)
	for mm in metamodes:
		r = re.match(r'\s*id=(\d+).*::\s*(.*)$', mm)
		if not r: continue
		id, line = int(r.group(1)), r.group(2)
		for dc in line.split(','):
			r = re.match(r'^\s*([^:]*)\s*:\s*(.*?)\s*$', dc)
			if not r: continue
			disp, mm = r.group(1), r.group(2)
			if disp not in displays and mm != 'NULL':
				print 'deleting incompatible modeline %d: %s'%(id,line)
				res = nv.delete_screen_metamode(screen, line)
				if not res: print ' - failed'


if __name__ == "__main__":
	main()

