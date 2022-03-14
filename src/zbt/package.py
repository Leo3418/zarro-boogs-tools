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

import pkgcore.ebuild.atom as atom
from pkgcore.ebuild.errors import MalformedAtom


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
