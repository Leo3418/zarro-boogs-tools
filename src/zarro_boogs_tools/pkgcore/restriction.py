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

from zarro_boogs_tools.pkgcore.profile import package_use_masked_in_profile

from typing import Optional

import pkgcore.ebuild.atom as atom
import pkgcore.restrictions.boolean as boolean
import pkgcore.restrictions.restriction as restriction
from pkgcore.ebuild.ebuild_src import package
from pkgcore.ebuild.profiles import OnDiskProfile
from pkgcore.restrictions.packages import Conditional


def preprocess_restriction(
        restrict: restriction.base,
        current_package: Optional[package] = None,
        profile: Optional[OnDiskProfile] = None,
        stable: Optional[bool] = None
) -> restriction.base:
    """
    Run a pkgcore restriction object through the preprocessing pipeline, so it
    can be converted into a form needed to support this program's operation.

    This function also has some optional parameters for filtering
    USE-conditional groups of a package based on the USE flag masks and forces
    for the package in a profile.  If none of the arguments for the
    'current_package', 'profile', and 'stable' parameters are 'None', then the
    restriction returned by this function will not contain any dependencies
    conditional upon USE settings not permitted by the profile.

    :param restrict: the instance of pkgcore's restriction class to process
    :param current_package: the package which has 'restrict' as a dependency in
        one of its dependency classes
    :param profile: the profile whose USE flag masks and forces are to be
        applied in USE-conditional group filtering
    :param stable: whether USE flag masks and forces for stable packages should
        be considered in USE-conditional group filtering
    :return: the preprocessing result
    """
    restrict = unwrap_use_conditional(
        restrict, current_package, profile, stable)
    restrict = strip_use_dep_from_restriction(restrict)
    return restrict


def unwrap_use_conditional(
        restrict: restriction.base,
        current_package: Optional[package] = None,
        profile: Optional[OnDiskProfile] = None,
        stable: Optional[bool] = None
) -> restriction.base:
    """
    Ensure the given restriction is not a USE-conditional group.  If it is,
    then the USE-conditional group will be converted into an unconditional
    all-of group and returned; otherwise, the restriction will be returned
    as-is.

    For a USE-conditional group such as
        java? ( >=virtual/jdk-1.8:* test? ( dev-java/junit:4 ) )
    this function effectively transforms it to the following all-of group:
        ( >=virtual/jdk-1.8:* dev-java/junit:4 )

    This function also has some optional parameters for filtering
    USE-conditional groups of a package based on the USE flag masks and forces
    for the package in a profile.  If none of the arguments for the
    'current_package', 'profile', and 'stable' parameters are 'None', then the
    restriction returned by this function will not contain any dependencies
    conditional upon USE settings not permitted by the profile.

    For example, if the 'test' USE flag is masked for 'current_package', then
    this function transforms the aforementioned USE-conditional group to the
    following all-of group instead:
        ( >=virtual/jdk-1.8:* )

    The purpose of this function is to promote these USE-conditional
    dependencies to generic ones, so when a package is being keyworded or
    stabilized, all the USE-conditional dependencies (or, if a profile is
    specified, all the dependencies for USE flags permitted by the profile) can
    have their keyword (either '**' or '~arch') accepted for testing, just like
    other generic, unconditional dependencies.

    The following restriction types are supported:
    - pkgcore.restrictions.packages.Conditional
    - pkgcore.ebuild.atom.atom
    - pkgcore.restrictions.boolean.AndRestriction
    - pkgcore.restrictions.boolean.OrRestriction
    These types shall cover every type of dependency specification permitted
    for package dependency classes in section 8.2, PMS for EAPI 8. For other
    types, this function behaves as an identity function: the returned
    restriction is identical to the restriction passed in.

    :param restrict: the instance of pkgcore's restriction class to process
    :param current_package: the package which has 'restrict' as a dependency in
        one of its dependency classes
    :param profile: the profile whose USE flag masks and forces are to be
        applied in USE-conditional group filtering
    :param stable: whether USE flag masks and forces for stable packages should
        be considered in USE-conditional group filtering
    :return: a transformed restriction that is guaranteed to not represent a
        USE-conditional group
    """
    if isinstance(restrict, Conditional):
        if restrict.attr == 'use' and \
                current_package is not None and \
                profile is not None and \
                stable is not None:
            # As per specification in section 8.2 of PMS for EAPI 8,
            # a USE-conditional group is defined with exactly one USE flag
            use_flag = set(restrict.restriction.vals).pop()
            if package_use_masked_in_profile(
                    current_package, use_flag, profile, stable):
                # The specified USE-conditional group never takes effect
                # because the USE flag is masked or forced
                return boolean.AndRestriction()

        payloads = list()
        for payload in restrict.payload:
            payloads.append(unwrap_use_conditional(
                payload, current_package, profile, stable))
        return boolean.AndRestriction(*payloads)
    elif isinstance(restrict, atom.atom):
        return restrict
    elif isinstance(restrict, boolean.AndRestriction) or \
            isinstance(restrict, boolean.OrRestriction):
        return type(restrict)(*map(
            lambda r: unwrap_use_conditional(
                r, current_package, profile, stable), restrict))
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

    The following restriction types are supported:
    - pkgcore.ebuild.atom.atom
    - pkgcore.restrictions.boolean.AndRestriction
    - pkgcore.restrictions.boolean.OrRestriction
    These types shall cover every type of dependency specification permitted
    for package dependency classes in section 8.2, PMS for EAPI 8, with the
    notable exception of pkgcore.restrictions.packages.Conditional, which shall
    be used only for USE-conditional groups for restrictions concerning
    packages.  For a Conditional restriction, please pass it to the
    'unwrap_use_conditional' function first, which transforms it to a
    restriction of one of the above types.  Then, the returned restriction can
    be passed to this function.

    For other types, this function behaves as an identity function: the
    returned restriction is identical to the restriction passed in.

    :param restrict: the instance of pkgcore's restriction class to process
    :return: a transformed restriction that is guaranteed to not have any USE
        dependency, under the condition that the original restriction's type is
        supported by this function
    """
    if isinstance(restrict, atom.atom):
        return restrict.no_usedeps
    elif isinstance(restrict, boolean.AndRestriction) or \
            isinstance(restrict, boolean.OrRestriction):
        return type(restrict)(*map(strip_use_dep_from_restriction, restrict))
    else:
        return restrict


def convert_and_restriction_to_list(and_restrict: boolean.AndRestriction) \
        -> list[restriction.base]:
    """
    Convert an AndRestriction, which shall represent an all-of group of
    dependencies, to a list containing all the child elements, in order.

    This function is helpful when the pkgcore.repository.prototype.tree.match()
    function is used to get the matching packages for each child element in an
    all-of group.  If an AndRestriction with zero or more than one child is
    passed to that function, it might not yield the expected result.  This
    function puts all the children of the AndRestriction into a list, so that
    function may be called against every element in the returned list.

    :param and_restrict: the AndRestriction object to be decomposed
    :return: a list containing all the child elements in 'and_restrict'
    """
    result = list()
    for child in and_restrict:
        if isinstance(child, boolean.AndRestriction) and \
                not isinstance(child, atom.atom):
            result.extend(convert_and_restriction_to_list(child))
        else:
            result.append(child)
    return result
