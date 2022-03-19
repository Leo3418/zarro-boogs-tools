#  zarro-boogs-tools Utility Functions Pertaining to Portage
#
#  Copyright (C) 2022 Yuan Liao
#  Copyright (C) 2022 zarro-boogs-tools Contributors
#
#  This file is part of zarro-boogs-tools.
#
#  zarro-boogs-tools is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  zarro-boogs-tools is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with zarro-boogs-tools.  If not, see
#  <https://www.gnu.org/licenses/>.

import os.path
import sys
from typing import Optional


def find_portage_config_root() -> Optional[str]:
    """
    Attempt to find the location for Portage configuration files in the current
    environment.

    :return: a string representation of the path to the Portage configuration
        files in the current environment, or 'None' if those files cannot be
        found
    """
    # Code stolen from pkgcore.ebuild.portage_conf.PortageConfig
    path = os.path.abspath(sys.prefix)
    # On GNU/Linux, the condition evaluates to 'True' when path == '/'
    while (parent := os.path.dirname(path)) != path:
        config_root = os.path.join(parent, 'etc/portage')
        if os.path.exists(config_root):
            return config_root
        path = parent
    return None
