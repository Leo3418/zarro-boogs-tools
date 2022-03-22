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
import zarro_boogs_tools.inference
import zarro_boogs_tools.package
from zarro_boogs_tools.cli import PortageConfigOperation

import os.path
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Optional

import pkgcore.ebuild.atom as atom
from nattka.bugzilla import BugCategory
from pkgcore.ebuild.ebuild_src import package
from pkgcore.ebuild.profiles import OnDiskProfile
from pkgcore.ebuild.repository import UnconfiguredTree


_pak = 'package.accept_keywords'


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
    program_name_abbrev = ''.join(map(
        lambda part: part[0], zarro_boogs_tools.__project_name__.split('-')))
    return f'zz-{program_name_abbrev}--'


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


def main(
        program_name: str,
        portage_config: Path,
        repo: UnconfiguredTree,
        atom_objs: list[atom.atom],
        target_profile: OnDiskProfile,
        keyword_change_type: Optional[BugCategory] = None,
        match_keyword: Optional[str] = None,
        portage_config_op: Optional[PortageConfigOperation] = None
) -> int:
    # If requested, clean any package list files created previously and exit
    if portage_config_op == PortageConfigOperation.CLEAN:
        qualified_pak = portage_config / _pak
        if len(atom_objs) == 0:
            for file_path in qualified_pak.glob(
                    f'{get_portage_config_file_prefix()}*'):
                file_path.unlink()
        else:
            for atom_obj in atom_objs:
                file_basename = get_accept_keywords_file_basename(atom_obj)
                file_path = qualified_pak / file_basename
                file_path.unlink(missing_ok=True)
        return 0

    # Select the best version for each requested atom
    atom_pkg_dict = dict()
    for atom_obj in atom_objs:
        main_package = zarro_boogs_tools.package.get_best_version(
            atom_obj, repo)
        if main_package is None:
            print(f"{program_name}: {atom_obj}: "
                  f"Could not find a matching package for atom",
                  file=sys.stderr)
            return 3
        atom_pkg_dict[atom_obj] = main_package

    # Determine target keyword
    arch = target_profile.arch
    if keyword_change_type is None:
        stable = zarro_boogs_tools.inference.is_stabilizing(
            atom_pkg_dict.values(), [arch])
    else:
        stable = keyword_change_type == BugCategory.STABLEREQ
    target_keyword = arch if stable else f'~{arch}'

    # Create package filter for dependencies
    if match_keyword is not None:
        pkg_filter = \
            zarro_boogs_tools.package.get_keyword_matching_pkg_filter(
                target_keyword, match_keyword)
    else:
        pkg_filter = \
            zarro_boogs_tools.package.get_keyword_matching_pkg_filter(
                target_keyword)

    # Output list of packages
    for atom_obj in atom_pkg_dict:
        pkgs_to_process = zarro_boogs_tools.package.get_packages_to_process(
            atom_pkg_dict[atom_obj], target_keyword, repo,
            pkg_filter, target_profile)
        file_contents = get_accept_keywords_contents(
            pkgs_to_process, target_keyword)
        for line in file_contents:
            print(line)
        if portage_config_op == PortageConfigOperation.WRITE:
            file_basename = get_accept_keywords_file_basename(atom_obj)
            file_path = portage_config / _pak / file_basename
            file_path.write_text(os.linesep.join(file_contents) + os.linesep)

    return 0
