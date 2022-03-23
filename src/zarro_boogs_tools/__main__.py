#  zarro-boogs-tools Main Entry Point
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

import zarro_boogs_tools.cli
import zarro_boogs_tools.inference
import zarro_boogs_tools.list
import zarro_boogs_tools.package

import sys
from pathlib import Path

import nattka.package
from pkgcore.ebuild.profiles import OnDiskProfile


def main(program_name: str, args: list[str]) -> int:
    opts = zarro_boogs_tools.cli.parse_args(args)
    repo_path = opts.repo
    portage_config_path = opts.portage_config  # 'None' OK
    match_keyword = opts.match_keyword
    keyword_change_type = opts.keyword_change_type

    domain, repo = nattka.package.find_repository(
        repo_path, portage_config_path)
    if portage_config_path is None:
        portage_config_path = Path(domain.config_dir)
    arch = domain.arch
    system_profile = domain.profile

    # Options commonly recognized by more than one subcommand but are not
    # always mandatory or recognized
    subcommand = opts.subcommand
    main_packages = list()
    if hasattr(opts, 'atoms'):
        for atom_str in opts.atoms:
            atom_obj = \
                zarro_boogs_tools.package.get_atom_obj_from_str(atom_str)
            check_result = \
                zarro_boogs_tools.package.check_atom_obj_for_keywording(
                    atom_obj)
            if check_result is not None:
                print(f"{program_name}: {atom_str}: {check_result}",
                      file=sys.stderr)
                return 1
            main_package = zarro_boogs_tools.package.get_best_version(
                atom_obj, repo)
            if main_package is None:
                print(f"{program_name}: {atom_obj}: "
                      f"Could not find a matching package for atom",
                      file=sys.stderr)
                return 3
            main_packages.append(main_package)

    if subcommand == 'ls':
        if opts.profile is None:
            profile = system_profile
        else:
            profile = None
            for repo_profile in repo.profiles.profiles:
                if opts.profile == repo_profile.path:
                    profile = OnDiskProfile(
                        repo_profile.base, repo_profile.path)
                    break
            if profile is None:
                print(f"{program_name}: Unknown profile: {opts.profile}",
                      file=sys.stderr)
                return 1
        clean = opts.clean
        ls_file_formats = opts.ls_file_formats
        return zarro_boogs_tools.list.main(
            portage_config_path, repo, main_packages, profile,
            keyword_change_type, match_keyword, clean, ls_file_formats)

    if subcommand == 'ls-nattka':
        print(f"{program_name}: {subcommand}: "
              f"Subcommand not fully implemented yet")
        return 0

    return 0


def main_wrapper() -> None:
    program_name = Path(sys.argv[0]).name
    sys.exit(main(program_name, sys.argv[1:]))


if __name__ == '__main__':
    main_wrapper()
