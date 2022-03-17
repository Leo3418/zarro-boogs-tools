#  zarro-boogs-tools Package Processing Functions
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

from typing import Callable, Iterable, Iterator, Optional

import nattka.package
import pkgcore.ebuild.atom as atom
from pkgcore.ebuild.ebuild_src import package
from pkgcore.ebuild.errors import MalformedAtom
from pkgcore.ebuild.repository import UnconfiguredTree


def get_atom_obj_from_str(atom_str: str) -> atom:
    """
    Convert a package atom specified in string to a corresponding object.  This
    function allows fuzzy '=' version operator: it accepts any atom that
    specifies an exact version but is not started with '='.  In other words,
    both '=foo-bar/baz-1.0.2' and 'foo-bar/baz-1.0.2' are accepted by this
    function and are treated in the same way.

    :param atom_str: the string representation of the atom
    :return: the object for the atom
    :raise MalformedAtom: if the specified atom is invalid by definition of
        this function
    """

    def str_to_atom():
        return atom.atom(atom_str, eapi='5')

    if atom_str.startswith('='):
        return str_to_atom()
    else:
        try:
            return str_to_atom()
        except MalformedAtom:
            atom_str = '=' + atom_str
            return str_to_atom()


def check_atom_obj_for_keywording(atom_obj: atom) -> Optional[str]:
    """
    Check if a package atom represented by an object is a valid atom in the
    context of keywording according to NATTkA
    <https://dev.gentoo.org/~mgorny/doc/nattka/bug.html>.  If it is, then this
    function returns 'None'; otherwise, a string describing the issue is
    returned.

    :param atom_obj: the object representing the atom
    :return: a string explaining the reason if the atom is invalid, or 'None'
        otherwise
    """
    if atom_obj is None:
        return "'None' is specified as the atom"
    if atom_obj.blocks:
        return "Atom contains a block operator"
    if atom_obj.slot_operator:
        return "Atom contains a slot operator"
    if atom_obj.use:
        return "Atom contains USE dependency"
    return None


def get_best_version(
        atom_obj: atom,
        repo: UnconfiguredTree,
        pkg_filter: Optional[Callable[[Iterator[package]], Iterable]] = None
) -> Optional[package]:
    """
    Find the best version of the package that satisfies the specified atom in
    a given ebuild repository.  If a version can be found, return the object
    that represents the best version; otherwise, 'None' is returned.

    :param atom_obj: the object representing the atom
    :param repo: the object representing the ebuild repository where candidate
        packages are searched
    :param pkg_filter: a filter for limiting the set of packages that may be
        selected as the best version; omit or specify 'None' to skip any
        filtering
    :return: the object for the best-matching package if there is one, or
        'None' otherwise
    """
    matches = repo.match(atom_obj, pkg_filter=pkg_filter)
    if len(matches) == 0:
        return None
    else:
        return nattka.package.select_best_version(matches)
