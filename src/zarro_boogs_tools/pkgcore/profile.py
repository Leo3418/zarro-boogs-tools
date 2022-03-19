#  zarro-boogs-tools Utility Functions for Portage Profiles
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

import os.path
from typing import Optional

from pkgcore.ebuild.ebuild_src import package
from pkgcore.ebuild.profiles import OnDiskProfile
from pkgcore.restrictions.restriction import AlwaysBool


def get_portage_profile(portage_config_root: str) -> Optional[OnDiskProfile]:
    """
    Find the Portage profile set in the specified Portage configuration files
    location.

    :param portage_config_root: a string representation of the path to the
        Portage configuration files
    :return: an object for the profile set in the specified Portage
        configuration if a valid profile is properly set, or 'None' otherwise
    """
    # Code stolen from pkgcore.ebuild.portage_conf.PortageConfig
    make_profile = os.path.join(portage_config_root, 'make.profile')
    if not os.path.islink(make_profile):
        return None
    profile_full_path = os.path.realpath(make_profile)
    base_path, profile = OnDiskProfile.split_abspath(profile_full_path)
    return OnDiskProfile(base_path, profile)


def package_use_masked_in_profile(
        queried_package: package,
        use_flag: str,
        profile: OnDiskProfile,
        stable: bool
) -> bool:
    """
    Determine whether a USE flag is masked for a package on the specified
    profile.

    A disabled USE flag may be in the form of either '-flag' or '!flag', and
    this function treats them in the same manner.  If a disabled USE flag
    (e.g. '-foo') is specified, then this function effectively returns whether
    'foo' is forced on the profile, since masking '-foo' is effectively
    equivalent to forcing 'foo'.

    Global USE flag restrictions (namely those specified in files use.mask,
    use.force, use.stable.mask, and use.stable.force, depending on the
    arguments for the 'use_flag' and 'stable' parameters) are respected by this
    function.

    :param queried_package: the package whose USE flag is queried
    :param use_flag: the USE flag whose masking state is queried
    :param profile: the profile where the masking state of the package's USE
        flag is queried
    :param stable: whether stable USE restrictions should be respected
    :return: whether the specified USE flag is masked for the package on the
        specified profile
    """
    negated_flag = use_flag.startswith('-') or use_flag.startswith('!')
    if negated_flag:
        normalized_flag = use_flag.lstrip('-').lstrip('!')
        use_dict = profile.forced_use.render_to_dict()
        if stable:
            use_dict.update(
                profile.stable_forced_use.render_to_dict())
    else:
        normalized_flag = use_flag
        use_dict = profile.masked_use.render_to_dict()
        if stable:
            use_dict.update(
                profile.stable_masked_use.render_to_dict())
    # The keys in the dictionaries for USE flag restrictions are
    # unversioned ${CATEGORY}/${PN} atoms represented by a string
    package_key = f'{queried_package.category}/{queried_package.PN}'
    # There might also be an entry for the global USE flag restrictions
    global_keys = set(filter(lambda k: isinstance(k, AlwaysBool),
                             use_dict.keys()))

    # Implement algorithm 5.1 in PMS for EAPI 8
    masked = False
    use_lines_for_package = list()
    # Process global restrictions first
    for global_key in global_keys:
        use_lines_for_package.extend(use_dict[global_key])
    use_lines_for_package.extend(use_dict.get(package_key, ()))
    matching_lines = filter(
        lambda e: e.key.match(queried_package), use_lines_for_package)
    for line in matching_lines:
        if normalized_flag in line.pos:
            masked = True
        elif normalized_flag in line.neg:
            masked = False
    return masked
