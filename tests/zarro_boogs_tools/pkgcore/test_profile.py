#  Unit tests for pkgcore/profile.py
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

import unittest
from zarro_boogs_tools.package import *
from zarro_boogs_tools.pkgcore.profile import *

import os.path
from pathlib import Path
from typing import Iterable

import nattka.package
from pkgcore.ebuild.profiles import OnDiskProfile


class TestProfile(unittest.TestCase):
    use_restrictions = None
    free0 = None
    free1 = None
    restricted0 = None
    restricted1 = None
    restricted_by_version0 = None
    restricted_by_version1 = None
    unrestricted_packages = None
    restricted_packages = None

    @classmethod
    def setUpClass(cls):
        test_repo_path = 'tests/ebuild-repos/use-restrictions'
        _, use_restrictions = nattka.package.find_repository(
            Path(test_repo_path))
        cls.use_restrictions = use_restrictions
        cls.profile = OnDiskProfile(
            os.path.join(test_repo_path, 'profiles'), 'default')
        cls.free0 = get_best_version(
            get_atom_obj_from_str('~app-misc/free-1.0.0'),
            cls.use_restrictions
        )
        cls.free1 = get_best_version(
            get_atom_obj_from_str('~app-misc/free-1.0.1'),
            cls.use_restrictions
        )
        cls.restricted0 = get_best_version(
            get_atom_obj_from_str('~app-misc/restricted-1.0.0'),
            cls.use_restrictions
        )
        cls.restricted1 = get_best_version(
            get_atom_obj_from_str('~app-misc/restricted-1.0.1'),
            cls.use_restrictions
        )
        cls.restricted_by_version0 = get_best_version(
            get_atom_obj_from_str('~app-misc/restricted-by-version-1.0.0'),
            cls.use_restrictions
        )
        cls.restricted_by_version1 = get_best_version(
            get_atom_obj_from_str('~app-misc/restricted-by-version-1.0.1'),
            cls.use_restrictions
        )
        cls.unrestricted_packages = [
            cls.free0, cls.free1,
            cls.restricted_by_version1
        ]
        cls.restricted_packages = [
            cls.restricted0, cls.restricted1,
            cls.restricted_by_version0
        ]
        cls.all_packages = \
            cls.unrestricted_packages + cls.restricted_packages

    def helper_package_use_masked_in_profile_against_packages(
            self,
            use_flag: str,
            packages: Iterable[package],
            masked_when_enabled_and_unstable: bool,
            masked_when_disabled_and_unstable: bool,
            masked_when_enabled_and_stable: bool,
            masked_when_disabled_and_stable: bool
    ):
        for pkg in packages:
            self.assertEqual(
                masked_when_enabled_and_unstable,
                package_use_masked_in_profile(
                    pkg, use_flag, self.profile, False))
            self.assertEqual(
                masked_when_disabled_and_unstable,
                package_use_masked_in_profile(
                    pkg, f'-{use_flag}', self.profile, False))
            self.assertEqual(
                masked_when_disabled_and_unstable,
                package_use_masked_in_profile(
                    pkg, f'!{use_flag}', self.profile, False))
            self.assertEqual(
                masked_when_enabled_and_stable,
                package_use_masked_in_profile(
                    pkg, use_flag, self.profile, True))
            self.assertEqual(
                masked_when_disabled_and_stable,
                package_use_masked_in_profile(
                    pkg, f'-{use_flag}', self.profile, True))
            self.assertEqual(
                masked_when_disabled_and_stable,
                package_use_masked_in_profile(
                    pkg, f'!{use_flag}', self.profile, True))

    def test_package_use_masked_in_profile_normal(self):
        """
        Test if the 'package_use_masked_in_profile' function returns the
        correct result for an unrestricted USE flag.
        """
        use_flag = 'normal'
        packages = self.all_packages
        masked_when_enabled_and_unstable = False
        masked_when_disabled_and_unstable = False
        masked_when_enabled_and_stable = False
        masked_when_disabled_and_stable = False
        self.helper_package_use_masked_in_profile_against_packages(
            use_flag, packages,
            masked_when_enabled_and_unstable,
            masked_when_disabled_and_unstable,
            masked_when_enabled_and_stable,
            masked_when_disabled_and_stable
        )

    def test_package_use_masked_in_profile_force(self):
        """
        Test if the 'package_use_masked_in_profile' function returns the
        correct result for a globally-forced USE flag.
        """
        use_flag = 'force'
        packages = self.all_packages
        masked_when_enabled_and_unstable = False
        masked_when_disabled_and_unstable = True
        masked_when_enabled_and_stable = False
        masked_when_disabled_and_stable = True
        self.helper_package_use_masked_in_profile_against_packages(
            use_flag, packages,
            masked_when_enabled_and_unstable,
            masked_when_disabled_and_unstable,
            masked_when_enabled_and_stable,
            masked_when_disabled_and_stable
        )

    def test_package_use_masked_in_profile_mask(self):
        """
        Test if the 'package_use_masked_in_profile' function returns the
        correct result for a globally-masked USE flag.
        """
        use_flag = 'mask'
        packages = self.all_packages
        masked_when_enabled_and_unstable = True
        masked_when_disabled_and_unstable = False
        masked_when_enabled_and_stable = True
        masked_when_disabled_and_stable = False
        self.helper_package_use_masked_in_profile_against_packages(
            use_flag, packages,
            masked_when_enabled_and_unstable,
            masked_when_disabled_and_unstable,
            masked_when_enabled_and_stable,
            masked_when_disabled_and_stable
        )

    def test_package_use_masked_in_profile_stable_force(self):
        """
        Test if the 'package_use_masked_in_profile' function returns the
        correct result for a globally-forced USE flag for stable packages.
        """
        use_flag = 'stable-force'
        packages = self.all_packages
        masked_when_enabled_and_unstable = False
        masked_when_disabled_and_unstable = False
        masked_when_enabled_and_stable = False
        masked_when_disabled_and_stable = True
        self.helper_package_use_masked_in_profile_against_packages(
            use_flag, packages,
            masked_when_enabled_and_unstable,
            masked_when_disabled_and_unstable,
            masked_when_enabled_and_stable,
            masked_when_disabled_and_stable
        )

    def test_package_use_masked_in_profile_stable_mask(self):
        """
        Test if the 'package_use_masked_in_profile' function returns the
        correct result for a globally-masked USE flag for stable packages.
        """
        use_flag = 'stable-mask'
        packages = self.all_packages
        masked_when_enabled_and_unstable = False
        masked_when_disabled_and_unstable = False
        masked_when_enabled_and_stable = True
        masked_when_disabled_and_stable = False
        self.helper_package_use_masked_in_profile_against_packages(
            use_flag, packages,
            masked_when_enabled_and_unstable,
            masked_when_disabled_and_unstable,
            masked_when_enabled_and_stable,
            masked_when_disabled_and_stable
        )

    def test_package_use_masked_in_profile_package_force(self):
        """
        Test if the 'package_use_masked_in_profile' function returns the
        correct result for a USE flag forced individually for some packages.
        """
        use_flag = 'pkg-force'
        packages = self.unrestricted_packages
        masked_when_enabled_and_unstable = False
        masked_when_disabled_and_unstable = False
        masked_when_enabled_and_stable = False
        masked_when_disabled_and_stable = False
        self.helper_package_use_masked_in_profile_against_packages(
            use_flag, packages,
            masked_when_enabled_and_unstable,
            masked_when_disabled_and_unstable,
            masked_when_enabled_and_stable,
            masked_when_disabled_and_stable
        )
        packages = self.restricted_packages
        masked_when_enabled_and_unstable = False
        masked_when_disabled_and_unstable = True
        masked_when_enabled_and_stable = False
        masked_when_disabled_and_stable = True
        self.helper_package_use_masked_in_profile_against_packages(
            use_flag, packages,
            masked_when_enabled_and_unstable,
            masked_when_disabled_and_unstable,
            masked_when_enabled_and_stable,
            masked_when_disabled_and_stable
        )

    def test_package_use_masked_in_profile_package_mask(self):
        """
        Test if the 'package_use_masked_in_profile' function returns the
        correct result for a USE flag masked individually for some packages.
        """
        use_flag = 'pkg-mask'
        packages = self.unrestricted_packages
        masked_when_enabled_and_unstable = False
        masked_when_disabled_and_unstable = False
        masked_when_enabled_and_stable = False
        masked_when_disabled_and_stable = False
        self.helper_package_use_masked_in_profile_against_packages(
            use_flag, packages,
            masked_when_enabled_and_unstable,
            masked_when_disabled_and_unstable,
            masked_when_enabled_and_stable,
            masked_when_disabled_and_stable
        )
        packages = self.restricted_packages
        masked_when_enabled_and_unstable = True
        masked_when_disabled_and_unstable = False
        masked_when_enabled_and_stable = True
        masked_when_disabled_and_stable = False
        self.helper_package_use_masked_in_profile_against_packages(
            use_flag, packages,
            masked_when_enabled_and_unstable,
            masked_when_disabled_and_unstable,
            masked_when_enabled_and_stable,
            masked_when_disabled_and_stable
        )

    def test_package_use_masked_in_profile_package_stable_force(self):
        """
        Test if the 'package_use_masked_in_profile' function returns the
        correct result for a USE flag forced individually for the stable
        versions of some packages.
        """
        use_flag = 'pkg-stable-force'
        packages = self.unrestricted_packages
        masked_when_enabled_and_unstable = False
        masked_when_disabled_and_unstable = False
        masked_when_enabled_and_stable = False
        masked_when_disabled_and_stable = False
        self.helper_package_use_masked_in_profile_against_packages(
            use_flag, packages,
            masked_when_enabled_and_unstable,
            masked_when_disabled_and_unstable,
            masked_when_enabled_and_stable,
            masked_when_disabled_and_stable
        )
        packages = self.restricted_packages
        masked_when_enabled_and_unstable = False
        masked_when_disabled_and_unstable = False
        masked_when_enabled_and_stable = False
        masked_when_disabled_and_stable = True
        self.helper_package_use_masked_in_profile_against_packages(
            use_flag, packages,
            masked_when_enabled_and_unstable,
            masked_when_disabled_and_unstable,
            masked_when_enabled_and_stable,
            masked_when_disabled_and_stable
        )

    def test_package_use_masked_in_profile_package_stable_mask(self):
        """
        Test if the 'package_use_masked_in_profile' function returns the
        correct result for a USE flag masked individually for the stable
        versions of some packages.
        """
        use_flag = 'pkg-stable-mask'
        packages = self.unrestricted_packages
        masked_when_enabled_and_unstable = False
        masked_when_disabled_and_unstable = False
        masked_when_enabled_and_stable = False
        masked_when_disabled_and_stable = False
        self.helper_package_use_masked_in_profile_against_packages(
            use_flag, packages,
            masked_when_enabled_and_unstable,
            masked_when_disabled_and_unstable,
            masked_when_enabled_and_stable,
            masked_when_disabled_and_stable
        )
        packages = self.restricted_packages
        masked_when_enabled_and_unstable = False
        masked_when_disabled_and_unstable = False
        masked_when_enabled_and_stable = True
        masked_when_disabled_and_stable = False
        self.helper_package_use_masked_in_profile_against_packages(
            use_flag, packages,
            masked_when_enabled_and_unstable,
            masked_when_disabled_and_unstable,
            masked_when_enabled_and_stable,
            masked_when_disabled_and_stable
        )


if __name__ == '__main__':
    unittest.main()
