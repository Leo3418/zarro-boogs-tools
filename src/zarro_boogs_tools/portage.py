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

import zarro_boogs_tools

import os.path
import sys
from collections.abc import Iterable
from typing import Optional

import pkgcore.ebuild.atom as atom
from pkgcore.ebuild.ebuild_src import package


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


def get_portage_config_file_prefix() -> str:
    """
    Get the prefix of files created by this program under /etc/portage.

    :return: the prefix of files created by this program under /etc/portage
    """
    program_name_abbrev = map(
        lambda part: part[0], zarro_boogs_tools.__project_name__.split('-'))
    return f'zz-{program_name_abbrev}-'


def get_accept_keywords_file_basename(atom_obj: atom) -> str:
    """
    Get a file name that identifies a package atom, does not contain any
    leading directory components, and is suitable for a file under
    /etc/portage/package.accept_keywords.

    :param atom_obj: the object representing the atom
    :return: a suitable file name identifying the atom for a file under
        /etc/portage/package.accept_keywords
    """
    file_name_atom = \
        f'{atom_obj.category}/{atom_obj.package}'.replace('/', '--')
    return f'{get_portage_config_file_prefix()}{file_name_atom}'


def get_accept_keywords_contents(
        packages: Iterable[package], target_keyword: str) -> Iterable[str]:
    """
    Get the lines to be added to /etc/portage/package.accept_keywords that
    allows the specified packages to be tested before the specified keyword can
    be applied to them.

    :param packages: the packages to test
    :param target_keyword: the keyword that the packages are expected to have
        after testing
    :return: the lines to be added to /etc/portage/package.accept_keywords to
        accept the current keywords for the specified packages
    """
    if target_keyword.startswith('~'):
        keyword_to_accept = '**'
    else:
        keyword_to_accept = f'~{target_keyword}'

    result = list()
    for pkg in packages:
        result.append(f'={pkg.cpvstr} {keyword_to_accept}')
    return result
