#!/bin/sh
###############################################################################
# disper hook - desktop notification on switch
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

case "$DISPER_STAGE" in
switch)
	if [ "$DISPER_LAYOUT" = "clone" ]; then
		TITLE="Clone displays"
		MESSAGE="$DISPER_DISPLAYS ($DISPER_BB_RESOLUTION)"
	else
		TITLE="Extend displays $DISPER_LAYOUT"
		MESSAGE=""
		for d in $DISPER_DISPLAYS; do
			r=$(eval echo $`echo DISPER_RESOLUTION_$d`)
			MESSAGE="$MESSAGE$d($r) "
		done
	fi
	notify-send -i disper "$TITLE" "$MESSAGE"
	;;
esac

