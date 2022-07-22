#!/bin/sh

# disper hook - show relevant environment variables for debugging
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

# This may be the only plugin that does not need to check for
# DISPER_STAGE at all.
echo "Disper hook environment for stage: $DISPER_STAGE"
env | sed 's|^\(DISPER_\)|  \1|p;d'

