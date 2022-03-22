#  zarro-boogs-tools Command-line Interface Module
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

from zarro_boogs_tools import __project_name__, __version__

import argparse
import enum
from pathlib import Path

from nattka.bugzilla import BugCategory


class PortageConfigOperation(enum.Enum):
    CLEAN = enum.auto()
    WRITE = enum.auto()


def parse_args(args: list[str], exit_on_error: bool = True) \
        -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        exit_on_error=exit_on_error
    )

    parser.add_argument(
        '--portage-config',
        metavar='DIR',
        type=Path,
        help="""
        use DIR as the Portage configuration files directory; (default:
        automatically-detected path, which will usually be
        ${EPREFIX}/etc/portage)
        """
    )
    parser.add_argument(
        '-r', '--repo',
        metavar='DIR',
        type=Path,
        default=Path('/var/db/repos/gentoo'),
        help="""
        use DIR as the Gentoo ebuild repository (default: %(default)s)
        """
    )
    parser.add_argument(
        '-m', '--match-keyword',
        metavar='KEYWORD',
        help="""
        for unkeyworded/unstable dependencies, if possible, use versions that
        have the specified KEYWORD
        """
    )

    group_keyword_change_type = parser.add_argument_group(
        title="options to control the type of keyword change",
        description="""
        If no '-k' or '-s' option is specified, then whether keywording or
        stabilization should be done will be inferred. If all specified
        packages are keyworded on every architecture in question, then this
        program will run as if '-s' was specified; otherwise, it will run as if
        '-k' was specified.
        """
    ).add_mutually_exclusive_group()
    group_keyword_change_type.add_argument(
        '-k', '--keyword',
        help="target the testing keyword ('~arch')",
        dest='keyword_change_type',
        action='store_const',
        const=BugCategory.KEYWORDREQ
    )
    group_keyword_change_type.add_argument(
        '-s', '--stable',
        help="target the stable keyword ('arch')",
        dest='keyword_change_type',
        action='store_const',
        const=BugCategory.STABLEREQ
    )

    parser.add_argument(
        '--version',
        action='version',
        help="output version information and exit",
        version=f"{__project_name__} {__version__}"
    )

    subparsers = parser.add_subparsers(
        dest='subcommand',
        required=True,
        title="available subcommands"
    )

    parser_ls_portage = subparsers.add_parser(
        'ls-portage',
        help="""
        find and list packages that need to be processed in Portage
        /etc/portage/package.accept_keywords format
        """,
        description="""
        In a format that can be used in /etc/portage/package.accept_keywords,
        list packages that need to be keyworded or stabilized in a keywording
        or stabilization request for the packages specified in the
        command-line.
        """
    )
    parser_ls_portage.add_argument(
        'atoms',
        help="package atoms to be processed",
        nargs='*',
    )
    parser_ls_portage.add_argument(
        '-p', '--profile',
        help="""
        the Portage profile to target; used to filter out USE-conditional
        dependencies for masked USE flags (default: the profile selected on the
        current system)
        """
    )
    group_ls_portage_action = parser_ls_portage.add_argument_group(
        title="options to alter Portage configuration files"
    ).add_mutually_exclusive_group()
    group_ls_portage_action.add_argument(
        '-w', '--write',
        help="""
        write the package list to package.accept_keywords/ under Portage
        configuration files directory
        """,
        dest='portage_config_op',
        action='store_const',
        const=PortageConfigOperation.WRITE
    )
    group_ls_portage_action.add_argument(
        '-c', '--clean',
        help="""
        clean files created by the '-w' option before; either clean all files
        ever created by '-w', or, if any packages are specified, only clean
        files fil created for those packages
        """,
        dest='portage_config_op',
        action='store_const',
        const=PortageConfigOperation.CLEAN
    )

    parser_ls_nattka = subparsers.add_parser(
        'ls-nattka',
        help="""
        find and list packages that need to be processed in NATTkA package list
        format
        """,
        description="""
        In a format that can be used in a NATTkA package list, list packages
        that need to be keyworded or stabilized in a keywording or
        stabilization request for the packages specified in the command-line.
        """
    )
    parser_ls_nattka.add_argument(
        'atoms',
        help="package atoms to be processed",
        nargs='+'
    )
    parser_ls_nattka.add_argument(
        '-a', '--arch',
        help="""
        the architectures concerned by the keywording or stabilization request;
        can be repeated to specify multiple architectures (default: the 'ARCH'
        Portage variable's value set on the system)
        """,
        action='append'
    )

    opts = parser.parse_args(args)
    return opts
