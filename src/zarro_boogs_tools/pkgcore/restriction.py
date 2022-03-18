#  zarro-boogs-tools Utility Functions for pkgcore Restriction Objects
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
import pkgcore.restrictions.boolean as boolean
import pkgcore.restrictions.restriction as restriction
from pkgcore.restrictions.packages import Conditional


def preprocess_restriction(restrict: restriction.base) -> restriction.base:
    """
    Run a pkgcore restriction object through the preprocessing pipeline, so it
    can be converted into a form needed to support this program's operation.

    :param restrict: the instance of pkgcore's restriction class to process
    :return: the preprocessing result
    """
    restrict = unwrap_use_conditional(restrict)
    restrict = strip_use_dep_from_restriction(restrict)
    return restrict


def unwrap_use_conditional(restrict: restriction.base) -> restriction.base:
    """
    Ensure the given restriction is not a USE-conditional group.  If it is,
    then the USE-conditional group will be converted into an unconditional
    all-of group and returned; otherwise, the restriction will be returned
    as-is.

    For a USE-conditional group such as
        python? ( ${PYTHON_DEPS} dev-python/requests[${PYTHON_USEDEP}] )
    this function effectively transforms it to the following all-of group:
        ( ${PYTHON_DEPS} dev-python/requests[${PYTHON_USEDEP}] )

    When a package is being keyworded or stabilized, all the USE-conditional
    dependencies for unmasked USE flags on the architecture in question needs
    to be tested as well.  The purpose of this function is to promote these
    USE-conditional dependencies to a generic one, so when the main packages
    being keyworded or stabilized that use those dependencies are being tested,
    the USE-conditional dependencies' keyword (either '**' or '~arch') can be
    accepted with other generic dependencies together.

    This does not interfere with USE flag masking.  For example, suppose a
    package has a USE-conditional group as 'java? ( >=virtual/jdk-1.8:* )', and
    it is being tested on an architecture where the 'java' USE flag is masked
    because JDK is not keyworded or stabilized on it.  Accepting the '**' or
    '~arch' keyword for >=virtual/jdk-1.8:* will not cause any changes because
    the USE flag mask is dictated by package.use.mask or
    package.use.stable.mask instead of the accepted keyword of the
    USE-conditional dependencies.

    :param restrict: the instance of pkgcore's restriction class to process
    :return: a transformed restriction that is guaranteed to not represent a
        USE-conditional group
    """
    if isinstance(restrict, Conditional):
        return boolean.AndRestriction(*restrict.payload)
    else:
        return restrict


def strip_use_dep_from_restriction(restrict: restriction.base) \
        -> restriction.base:
    """
    Ensure the given restriction does not contain any USE dependency
    specification.  If it does, and the restriction's type is supported by this
    function, then the USE dependency will be removed, and the resulting
    restriction will be returned; otherwise, the restriction will be returned
    as-is.

    For an atom with USE dependency such as
        >=virtual/jdk-1.8:*[-headless-awt]
    this function effectively transforms it to
        >=virtual/jdk-1.8:*

    This transformation might be necessary to prevent pkgcore from failing to
    get a specific package that matches the atom.  If pkgcore cannot find such
    a package directly due to presence of the USE dependency, it might traverse
    all the packages in the ebuild repository, which will result in
    unacceptably-long program execution time for repositories as large as
    ::gentoo.

    The following restriction types are supported, and they shall cover every
    type of dependency specification permitted for package dependency classes
    in section 8.2, PMS for EAPI 8:
    - pkgcore.ebuild.atom.atom
    - pkgcore.restrictions.boolean.AndRestriction
    - pkgcore.restrictions.boolean.OrRestriction
    For other types, this function behaves as an identity function: the
    returned restriction is identical to the restriction passed in.

    :param restrict: the instance of pkgcore's restriction class to process
    :return: a transformed restriction that is guaranteed to not have any USE
        dependency, under the condition that the original restriction's type is
        supported by this function
    """

    def process_children(
            boolean_restrict: boolean.base,
            restriction_type: type
    ) -> restriction.base:
        restrictions_without_use = list()
        for child in boolean_restrict:
            child = preprocess_restriction(child)
            restrictions_without_use.append(child)
        return restriction_type(*restrictions_without_use)

    if isinstance(restrict, atom.atom):
        return restrict.no_usedeps
    elif isinstance(restrict, boolean.AndRestriction):
        return process_children(restrict, boolean.AndRestriction)
    elif isinstance(restrict, boolean.OrRestriction):
        return process_children(restrict, boolean.OrRestriction)
    else:
        return restrict
