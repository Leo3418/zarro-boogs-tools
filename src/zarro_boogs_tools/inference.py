#  zarro-boogs-tools Optional Command-line Arguments Inference Module
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

from collections.abc import Iterable

from pkgcore.ebuild.ebuild_src import package


def is_stabilizing(packages: Iterable[package], arches: Iterable[str]) -> bool:
    """
    Infer whether keywording or stabilization is intended to be done based on
    the given packages' keywords on the specified architectures.  If all the
    specified packages are keyworded on the specified architectures, then it is
    inferred that a stabilization is to be done; otherwise, it would be
    regarded as keywording is to be done.

    :param packages: the packages to be keyworded or stabilized
    :param arches: the architecture names where keywording or stabilization is
        to happen
    :return: 'True' if it is inferred that stabilization is to be done, or
        'False' if keywording is inferred to be done
    """
    for arch in arches:
        stable_keyword = arch
        unstable_keyword = f'~{arch}'
        for pkg in packages:
            keywords = pkg.keywords
            pkg_keyworded_on_arch = stable_keyword in keywords or \
                unstable_keyword in keywords
            if not pkg_keyworded_on_arch:
                # Stabilization should take place only when every package is
                # keyworded on every specified architecture
                return False
    return True
