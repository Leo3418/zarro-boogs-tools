#  zarro-boogs-tools Functions Pertaining to the 'ls' Subcommand
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

from zarro_boogs_tools import __project_name_abbrev__
from zarro_boogs_tools.inference import is_stabilizing
from zarro_boogs_tools.package import \
    get_keyword_matching_pkg_filter, get_packages_to_process
from zarro_boogs_tools.portage import \
    PAK, get_portage_config_file_prefix, get_accept_keywords_contents

import enum
import os
from collections.abc import Iterable
from pathlib import Path
from typing import Optional

from nattka.bugzilla import BugCategory
from pkgcore.ebuild.ebuild_src import package
from pkgcore.ebuild.profiles import OnDiskProfile
from pkgcore.ebuild.repository import UnconfiguredTree


class PackageListFileFormat(enum.Enum):
    """Enumeration of supported package list file formats."""
    PORTAGE = enum.auto()
    TATT = enum.auto()


def get_package_list_file_name_from_package(main_package: package) -> str:
    """
    Get a file name component that may be used to identify the package list
    file for a main package, does not contain any leading directory components,
    and does not render the file as a hidden file when it is used as a prefix
    of a file's base name.

    :param main_package: the main package that identifies a package list
    :return: a suitable file name identifying the main package
    """
    return f'{main_package.category}/{main_package.PN}'.replace('/', '--')


def get_target_keyword(
        target_profile: OnDiskProfile,
        main_packages: Iterable[package],
        keyword_change_type: Optional[BugCategory] = None
) -> str:
    """
    Get the keyword that the specified main packages will have after the
    ongoing keywording or stabilization task based on the profile on which the
    testing would be done.  If the type of the keyword change (keywording vs.
    stabilization) is not explicitly specified, then it will be inferred based
    on the current keywords the main packages have in common.

    :param target_profile: the profile selected on the testing environment for
        the keywording or stabilization task
    :param main_packages: the main packages to keyword or stabilize
    :param keyword_change_type: the type of keyword change to perform; omit or
        specify 'None' to have the type be inferred according to the keywords
        of the 'main_packages'
    :return: the keyword that the main packages are eligible for after they are
        tested on a system with the specified target profile selected
    """
    arch = target_profile.arch
    if keyword_change_type is None:
        stable = is_stabilizing(main_packages, [arch])
    else:
        stable = keyword_change_type == BugCategory.STABLEREQ
    return arch if stable else f'~{arch}'


def get_package_lists(
        repo: UnconfiguredTree,
        main_packages: Iterable[package],
        target_profile: OnDiskProfile,
        target_keyword: str,
        match_keyword: Optional[str] = None
) -> dict[package, list[package]]:
    """
    For each of the specified main packages to keyword or stabilize for a
    Portage profile, make a list of all packages (including dependencies) that
    need to be keyworded or stabilized at the same time.

    :param repo: the object representing the ebuild repository where candidate
        packages are searched
    :param main_packages: the main packages to keyword or stabilize
    :param target_profile: the profile to apply USE flag restrictions when
        dependencies are being selected
    :param target_keyword: the keyword that the main packages will have after
        the keywording or stabilization process
    :param match_keyword: if not omitted or not 'None', for unkeyworded or
        unstable dependencies, use versions that are visible on the specified
        keyword if possible
    :return: a dictionary that maps each package in 'main_packages' to the list
        of all packages that need to be processed for keywording or stabilizing
        the package
    """
    # Create package filter for dependencies
    if match_keyword is not None:
        pkg_filter = get_keyword_matching_pkg_filter(
            target_keyword, match_keyword)
    else:
        pkg_filter = get_keyword_matching_pkg_filter(target_keyword)

    # Compute result
    result = dict()
    for pkg in main_packages:
        result[pkg] = get_packages_to_process(
            pkg, target_keyword, repo, pkg_filter, target_profile)
    return result


def write_file_with_eperm_fallback(
        contents: str, primary_path: Path, fallback_path: Path) -> None:
    """
    Attempt to write a string to a file at the specified primary path first; if
    the operation fails because of insufficient permission, write it to a file
    at the fallback path instead.

    :param contents: the string to be written to a file
    :param primary_path: the first path to attempt for the new file
    :param fallback_path: the next path to attempt if permission to write to
        the primary path is denied
    """
    try:
        primary_path.parent.mkdir(exist_ok=True)
        primary_path.write_text(contents)
    except PermissionError:
        fallback_path.parent.mkdir(exist_ok=True)
        fallback_path.write_text(contents)


def main(
        portage_config: Path,
        repo: UnconfiguredTree,
        main_packages: list[package],
        target_profile: OnDiskProfile,
        keyword_change_type: Optional[BugCategory] = None,
        match_keyword: Optional[str] = None,
        clean: bool = False,
        ls_file_formats: list[PackageListFileFormat] = None
) -> int:
    # If requested, clean any package list files created previously and exit
    if clean:
        file_paths_to_clean = list()
        if len(main_packages) == 0:
            # Every file selected by the glob pattern for removal should exist
            missing_ok = False
            # Package list files for Portage
            file_paths_to_clean.extend((portage_config / PAK).glob(
                f'{get_portage_config_file_prefix()}*'))
            file_paths_to_clean.extend(Path(PAK).glob(
                f'{get_portage_config_file_prefix()}*'))
            # Package list files for tatt
            file_paths_to_clean.extend(Path('.').glob(
                f'{__project_name_abbrev__}--*'))
        else:
            missing_ok = True
            for pkg in main_packages:
                pkg_id = get_package_list_file_name_from_package(pkg)
                # Package list files for Portage
                file_paths_to_clean.append(
                    (portage_config / PAK) /
                    f'{get_portage_config_file_prefix()}{pkg_id}')
                file_paths_to_clean.append(
                    Path(PAK) / f'{get_portage_config_file_prefix()}{pkg_id}')
                # Package list files for tatt
                file_paths_to_clean.append(
                    Path('.') / f'{__project_name_abbrev__}--{pkg_id}')
        for file_path in file_paths_to_clean:
            file_path.unlink(missing_ok)
        return 0

    if ls_file_formats is None:
        ls_file_formats = list()

    # Determine target keyword
    target_keyword = get_target_keyword(
        target_profile, main_packages, keyword_change_type)

    # Get and output package lists
    pkg_to_list_dict = get_package_lists(
        repo, main_packages, target_profile, target_keyword, match_keyword)
    for main_package in pkg_to_list_dict:
        package_list = pkg_to_list_dict[main_package]
        # Print package list to standard output in Portage
        # package.accept_keywords format
        portage_pak_contents = get_accept_keywords_contents(
            package_list, target_keyword)
        for line in portage_pak_contents:
            print(line)

        pkg_id = get_package_list_file_name_from_package(main_package)
        for ls_file_format in ls_file_formats:
            if ls_file_format == PackageListFileFormat.PORTAGE:
                write_file_with_eperm_fallback(
                    os.linesep.join(portage_pak_contents) + os.linesep,
                    portage_config / PAK /
                    f'{get_portage_config_file_prefix()}{pkg_id}',
                    Path(PAK) / f'{get_portage_config_file_prefix()}{pkg_id}'
                )
            if ls_file_format == PackageListFileFormat.TATT:
                file_path = Path('.') / f'{__project_name_abbrev__}--{pkg_id}'
                file_contents = os.linesep.join(
                    map(lambda p: f'={p.cpvstr}', reversed(package_list)))
                file_path.write_text(file_contents + os.linesep)

    return 0
