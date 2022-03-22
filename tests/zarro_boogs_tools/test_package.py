#  Unit tests for package.py
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

from . import unittest
from zarro_boogs_tools.package import *

import os.path
from pathlib import Path

import nattka.package
from pkgcore.ebuild.profiles import OnDiskProfile


class TestPackage(unittest.TestCase):
    def test_get_atom_obj_from_str_pms(self):
        """
        Test if the 'get_atom_obj_from_str' function supports all kinds of
        package atoms defined by section 8.3, PMS for EAPI 8.
        """
        self.assertIsNotNone(get_atom_obj_from_str('foo-bar/baz'))

        # 8.3.1 Operators
        self.assertIsNotNone(get_atom_obj_from_str('<foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('<foo-bar/baz-1.0.2-r1'))
        self.assertIsNotNone(get_atom_obj_from_str('<=foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('<=foo-bar/baz-1.0.2-r1'))
        self.assertIsNotNone(get_atom_obj_from_str('=foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('=foo-bar/baz-1.0.2-r1'))
        self.assertIsNotNone(get_atom_obj_from_str('=foo-bar/baz-1.0*'))
        self.assertIsNotNone(get_atom_obj_from_str('~foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('>foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('>foo-bar/baz-1.0.2-r1'))
        self.assertIsNotNone(get_atom_obj_from_str('>=foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('>=foo-bar/baz-1.0.2-r1'))

        # 8.3.3 Slot dependencies
        self.assertIsNotNone(get_atom_obj_from_str('foo-bar/baz:1'))
        self.assertIsNotNone(get_atom_obj_from_str('foo-bar/baz:1/2'))
        self.assertIsNotNone(get_atom_obj_from_str('foo-bar/baz:*'))
        self.assertIsNotNone(get_atom_obj_from_str('foo-bar/baz:='))
        self.assertIsNotNone(get_atom_obj_from_str('foo-bar/baz:1='))
        self.assertIsNotNone(get_atom_obj_from_str('foo-bar/baz:1/2='))

        # 8.3.2 Block operator
        self.assertIsNotNone(get_atom_obj_from_str('!foo-bar/baz'))
        self.assertIsNotNone(get_atom_obj_from_str('!<foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('!<=foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('!=foo-bar/baz-1.0*'))
        self.assertIsNotNone(get_atom_obj_from_str('!=foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('!~foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('!>foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('!>=foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('!foo-bar/baz:1'))
        self.assertIsNotNone(get_atom_obj_from_str('!foo-bar/baz:1/2'))
        self.assertIsNotNone(get_atom_obj_from_str('!foo-bar/baz:*'))
        self.assertIsNotNone(get_atom_obj_from_str('!!foo-bar/baz'))
        self.assertIsNotNone(get_atom_obj_from_str('!!<foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('!!<=foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('!!=foo-bar/baz-1.0*'))
        self.assertIsNotNone(get_atom_obj_from_str('!!=foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('!!~foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('!!>foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('!!>=foo-bar/baz-1.0.2'))
        self.assertIsNotNone(get_atom_obj_from_str('!!foo-bar/baz:1'))
        self.assertIsNotNone(get_atom_obj_from_str('!!foo-bar/baz:1/2'))
        self.assertIsNotNone(get_atom_obj_from_str('!!foo-bar/baz:*'))

        # 8.3.4 USE dependencies
        self.assertIsNotNone(get_atom_obj_from_str('foo-bar/baz[qux]'))
        self.assertIsNotNone(get_atom_obj_from_str('foo-bar/baz[qux=]'))
        self.assertIsNotNone(get_atom_obj_from_str('foo-bar/baz[!qux=]'))
        self.assertIsNotNone(get_atom_obj_from_str('foo-bar/baz[qux?]'))
        self.assertIsNotNone(get_atom_obj_from_str('foo-bar/baz[!qux?]'))
        self.assertIsNotNone(get_atom_obj_from_str('foo-bar/baz[-qux]'))
        self.assertIsNotNone(
            get_atom_obj_from_str('foo-bar/baz[first,-second,third?]'))
        self.assertIsNotNone(get_atom_obj_from_str('foo-bar/baz[qux(+)]'))
        self.assertIsNotNone(get_atom_obj_from_str('foo-bar/baz[qux(-)]'))

    def test_get_atom_obj_from_str_fuzzy_equals(self):
        """
        Test if the 'get_atom_obj_from_str' function treats an atom without an
        operator but with a version specification as if the '=' operator was
        used.
        """
        pms_compliant_atom = '=foo-bar/baz-1.0.2'
        expected = get_atom_obj_from_str(pms_compliant_atom)
        self.assertIsNotNone(expected)
        actual = get_atom_obj_from_str(pms_compliant_atom.strip('='))
        self.assertEqual(expected, actual)

    def test_get_atom_obj_from_str_pms_exception(self):
        """
        Test if the 'get_atom_obj_from_str' function raises the expected type
        of exception upon an invalid atom.
        """
        with self.assertRaises(MalformedAtom):
            get_atom_obj_from_str('=foo-bar/baz')
        with self.assertRaises(MalformedAtom):
            get_atom_obj_from_str('?foo-bar/baz')
        with self.assertRaises(MalformedAtom):
            get_atom_obj_from_str('?=foo-bar/baz')
        with self.assertRaises(MalformedAtom):
            get_atom_obj_from_str('foo-bar/baz:')
        with self.assertRaises(MalformedAtom):
            get_atom_obj_from_str('!!!foo-bar/baz')

    def test_check_atom_obj_for_keywording(self):
        """
        Test if the 'check_atom_obj_for_keywording' function returns 'None' for
        atoms that are valid in the context of keywording and a string for
        invalid atoms.
        """
        self.assertIsNone(check_atom_obj_for_keywording(
            get_atom_obj_from_str('dev-python/pytest')))
        self.assertIsNone(check_atom_obj_for_keywording(
            get_atom_obj_from_str('<dev-python/pytest-5')))
        self.assertIsNone(check_atom_obj_for_keywording(
            get_atom_obj_from_str('>=virtual/jdk-1.8')))
        self.assertIsNone(check_atom_obj_for_keywording(
            get_atom_obj_from_str('sys-devel/llvm:10')))
        self.assertIsNone(check_atom_obj_for_keywording(
            get_atom_obj_from_str('app-misc/frobnicate-1.2.3')))
        self.assertIsNone(check_atom_obj_for_keywording(
            get_atom_obj_from_str('=dev-libs/libfrobnicate-1.9')))

        self.assertIsNotNone(check_atom_obj_for_keywording(
            get_atom_obj_from_str('!dev-java/kotlin-stdlib:1.6')))
        self.assertIsNotNone(check_atom_obj_for_keywording(
            get_atom_obj_from_str('!!dev-java/kotlin-stdlib:1.6')))
        self.assertIsNotNone(check_atom_obj_for_keywording(
            get_atom_obj_from_str('>=virtual/jdk-1.8:*')))
        self.assertIsNotNone(check_atom_obj_for_keywording(
            get_atom_obj_from_str('dev-libs/libffi:=')))
        self.assertIsNotNone(check_atom_obj_for_keywording(
            get_atom_obj_from_str('media-sound/sox[ogg]')))

    def test_get_best_version(self):
        """
        Test if the 'get_best_version' function returns a matching version for
        atoms that have a match in the specified ebuild repository and 'None'
        otherwise.
        """
        _, empty = nattka.package.find_repository(
            Path('tests/ebuild-repos/empty'))
        _, single_pkg_multi_vers = nattka.package.find_repository(
            Path('tests/ebuild-repos/single-pkg-multi-vers'))

        self.assertIsNone(get_best_version(
            get_atom_obj_from_str('foo-bar/baz'), empty))
        self.assertIsNone(get_best_version(
            get_atom_obj_from_str('foo-bar/qux'), empty))

        self.assertIsNone(get_best_version(
            get_atom_obj_from_str('foo-bar/qux'), single_pkg_multi_vers))
        self.assertIsNone(get_best_version(
            get_atom_obj_from_str('>=foo-bar/baz-1.1'), single_pkg_multi_vers))
        self.assertIsNone(get_best_version(
            get_atom_obj_from_str('foo-bar/baz:2'), single_pkg_multi_vers))
        self.assertEqual('1.0.3', get_best_version(
            get_atom_obj_from_str('foo-bar/baz'), single_pkg_multi_vers
        ).version)
        self.assertEqual('1.0.2', get_best_version(
            get_atom_obj_from_str('=foo-bar/baz-1.0.2'), single_pkg_multi_vers
        ).version)

    def test_get_best_version_pkg_filter(self):
        """
        Test if the 'get_best_version' function respects any specified package
        filter.
        """
        _, single_pkg_multi_vers = nattka.package.find_repository(
            Path('tests/ebuild-repos/single-pkg-multi-vers'))

        self.assertEqual('1.0.2', get_best_version(
            get_atom_obj_from_str('foo-bar/baz'), single_pkg_multi_vers,
            lambda ps: filter(lambda p: p.version == '1.0.2', ps)
        ).version)
        self.assertIsNone(get_best_version(
            get_atom_obj_from_str('>foo-bar/baz-1.0.2'), single_pkg_multi_vers,
            lambda ps: filter(lambda p: p.version == '1.0.2', ps)))

    def test_get_packages_to_process(self):
        """
        Run a basic test for the 'get_packages_to_process' function.
        """
        _, etr_simplified = nattka.package.find_repository(
            Path('tests/ebuild-repos/etr-simplified'))
        etr = get_best_version(
            get_atom_obj_from_str('games-action/extreme-tuxracer'),
            etr_simplified
        )
        etr_pkgs = get_packages_to_process(etr, '~riscv', etr_simplified)
        self.assertEqual(2, len(etr_pkgs))
        etr_pkgs_strs = [pkg.cpvstr for pkg in etr_pkgs]
        self.assertTrue(
            'games-action/extreme-tuxracer-0.8.1_p1' in etr_pkgs_strs)
        self.assertTrue('media-sound/modplugtools-0.5.3' in etr_pkgs_strs)

    def test_get_packages_to_process_pkg_filter(self):
        """
        Test if the 'get_packages_to_process' function respects version
        preference specified with the 'pkg_filter' parameter.
        """
        _, java = nattka.package.find_repository(
            Path('tests/ebuild-repos/java'))
        ant_core = get_best_version(
            get_atom_obj_from_str('dev-java/ant-core'), java)
        target_keyword = '~riscv'
        ant_core_pkgs = get_packages_to_process(
            ant_core, target_keyword, java,
            lambda pkgs: filter(
                lambda pkg:
                target_keyword in pkg.keywords or 'amd64' in pkg.keywords,
                pkgs)
        )
        self.assertEqual(4, len(ant_core_pkgs))
        ant_core_pkgs_strs = [pkg.cpvstr for pkg in ant_core_pkgs]
        self.assertTrue('dev-java/ant-core-1.10.9-r3' in ant_core_pkgs_strs)
        self.assertTrue('virtual/jdk-11-r2' in ant_core_pkgs_strs)
        self.assertTrue('dev-java/openjdk-bin-11.0.14_p9-r1'
                        in ant_core_pkgs_strs)
        self.assertTrue('sec-policy/selinux-java-2.20210908-r1'
                        in ant_core_pkgs_strs)

    def test_get_packages_to_process_profile(self):
        """
        Test if the 'get_packages_to_process' function respects USE flag
        restrictions in the profile specified with the 'profile' parameter.
        """
        java_path = 'tests/ebuild-repos/java'
        _, java = nattka.package.find_repository(Path(java_path))
        ant_core = get_best_version(
            get_atom_obj_from_str('dev-java/ant-core'), java)
        # This profile masks the 'selinux' USE flag, so no SELinux-related
        # dependency should be included in the result
        profile = OnDiskProfile(os.path.join(java_path, 'profiles'), 'base')
        target_keyword = '~riscv'
        ant_core_pkgs = get_packages_to_process(
            ant_core, target_keyword, java,
            lambda pkgs: filter(
                lambda pkg:
                target_keyword in pkg.keywords or 'amd64' in pkg.keywords,
                pkgs),
            profile
        )
        self.assertEqual(3, len(ant_core_pkgs))
        ant_core_pkgs_strs = [pkg.cpvstr for pkg in ant_core_pkgs]
        self.assertTrue('dev-java/ant-core-1.10.9-r3' in ant_core_pkgs_strs)
        self.assertTrue('virtual/jdk-11-r2' in ant_core_pkgs_strs)
        self.assertTrue('dev-java/openjdk-bin-11.0.14_p9-r1'
                        in ant_core_pkgs_strs)

    def test_get_packages_to_process_profile_stable(self):
        """
        Test if the 'get_packages_to_process' function respects USE flag
        restrictions exclusively for stable packages in the profile specified
        with the 'profile' parameter when a package is stabilized.
        """
        use_restrictions_path = 'tests/ebuild-repos/use-restrictions'
        _, use_restrictions = nattka.package.find_repository(
            Path(use_restrictions_path))
        restricted = get_best_version(
            get_atom_obj_from_str('=app-misc/restricted-1.0.1'),
            use_restrictions
        )
        profile = OnDiskProfile(
            os.path.join(use_restrictions_path, 'profiles'), 'default')
        target_keyword = 'x86'
        restricted_pkgs = get_packages_to_process(
            restricted, target_keyword, use_restrictions, None, profile)
        self.assertEqual(6, len(restricted_pkgs))
        restricted_pkgs_strs = [pkg.cpvstr for pkg in restricted_pkgs]
        # Neither dev-libs/stable-mask nor dev-libs/pkg-stable-mask is expected
        self.assertTrue('app-misc/restricted-1.0.1' in restricted_pkgs_strs)
        self.assertTrue('dev-libs/force-0' in restricted_pkgs_strs)
        self.assertTrue('dev-libs/normal-0' in restricted_pkgs_strs)
        self.assertTrue('dev-libs/pkg-force-0' in restricted_pkgs_strs)
        self.assertTrue('dev-libs/pkg-stable-force-0' in restricted_pkgs_strs)
        self.assertTrue('dev-libs/stable-force-0' in restricted_pkgs_strs)

    def test_get_packages_to_process_ignores_blocker(self):
        """
        Test if the 'get_packages_to_process' function does not return
        dependencies specified as a block.
        """
        _, etr_simplified = nattka.package.find_repository(
            Path('tests/ebuild-repos/etr-simplified'))
        pkgconf = get_best_version(
            get_atom_obj_from_str('dev-util/pkgconf'), etr_simplified)
        pkgconf_pkgs = get_packages_to_process(
            pkgconf, 'riscv', etr_simplified)
        self.assertEqual(1, len(pkgconf_pkgs))
        pkgconf_pkgs_strs = [pkg.cpvstr for pkg in pkgconf_pkgs]
        self.assertTrue('dev-util/pkgconf-1.8.0-r1' in pkgconf_pkgs_strs)

    def test_get_packages_to_process_treats_stable_as_keyworded(self):
        """
        Test if the 'get_packages_to_process' function does not add a
        dependency that has already been stabilized in a keywording process.
        There is no need to keyword a stable package; stable packages should
        obviously be considered keyworded.
        """
        _, java = nattka.package.find_repository(
            Path('tests/ebuild-repos/java'))
        c3p0 = get_best_version(get_atom_obj_from_str('dev-java/c3p0'), java)
        c3p0_pkgs = get_packages_to_process(
            c3p0, '~arm64', java,
            lambda pkgs: filter(lambda pkg: 'arm64' in pkg.keywords, pkgs))
        self.assertEqual(1, len(c3p0_pkgs))
        c3p0_pkgs_strs = [pkg.cpvstr for pkg in c3p0_pkgs]
        self.assertTrue('dev-java/c3p0-0.9.5.5-r1' in c3p0_pkgs_strs)

    def test_get_keyword_matching_pkg_filter(self):
        """
        Test if the filter returned by the 'get_keyword_matching_pkg_filter'
        function filters out packages that are not visible on any specified
        keyword in the arguments.
        """
        _, java = nattka.package.find_repository(
            Path('tests/ebuild-repos/java'))
        pkg_filter_uriscv = get_keyword_matching_pkg_filter(
            '~riscv')
        pkg_filter_uriscv_uamd64 = get_keyword_matching_pkg_filter(
            '~riscv', '~amd64')
        pkg_filter_uriscv_amd64 = get_keyword_matching_pkg_filter(
            '~riscv', 'amd64')
        pkg_filter_uamd64 = get_keyword_matching_pkg_filter(
            '~amd64')
        pkg_filter_uamd64_amd64 = get_keyword_matching_pkg_filter(
            '~amd64', 'amd64')
        pkg_filter_amd64 = get_keyword_matching_pkg_filter(
            'amd64')
        musl_atom = get_atom_obj_from_str('sys-libs/musl')
        jdk_atom = get_atom_obj_from_str('virtual/jdk')
        glibc_atom = get_atom_obj_from_str('sys-libs/glibc')

        self.assertEqual('1.2.2-r8', get_best_version(
            musl_atom, java, pkg_filter_uriscv).PVR)
        self.assertEqual('1.2.2-r8', get_best_version(
            musl_atom, java, pkg_filter_uriscv_uamd64).PVR)
        self.assertEqual('1.2.2-r8', get_best_version(
            musl_atom, java, pkg_filter_uriscv_amd64).PVR)
        self.assertIsNone(get_best_version(
            jdk_atom, java, pkg_filter_uriscv))
        self.assertEqual('17', get_best_version(
            jdk_atom, java, pkg_filter_uriscv_uamd64).PVR)
        self.assertEqual('11-r2', get_best_version(
            jdk_atom, java, pkg_filter_uriscv_amd64).PVR)
        self.assertEqual('2.34-r10', get_best_version(
            glibc_atom, java, pkg_filter_uamd64).PVR)
        self.assertEqual('2.34-r10', get_best_version(
            glibc_atom, java, pkg_filter_uamd64_amd64).PVR)
        self.assertEqual('2.33-r13', get_best_version(
            glibc_atom, java, pkg_filter_amd64).PVR)

    def test_get_keyword_matching_pkg_filter_unstable_older_than_stable(self):
        """
        Test if the filter returned by the 'get_keyword_matching_pkg_filter'
        function returns the latest stable version of a package when the
        package has an older unstable version.
        """
        _, java = nattka.package.find_repository(
            Path('tests/ebuild-repos/java'))
        pkg_filter_uriscv_uarm64 = get_keyword_matching_pkg_filter(
            '~riscv', '~arm64')
        pkg_filter_uriscv_arm64 = get_keyword_matching_pkg_filter(
            '~riscv', 'arm64')
        pkg_filter_arm_uarm64 = get_keyword_matching_pkg_filter(
            'arm', '~arm64')
        pkg_filter_arm_arm64 = get_keyword_matching_pkg_filter(
            'arm', 'arm64')
        antlr4_atom = get_atom_obj_from_str('dev-java/antlr:4')

        self.assertEqual('4.9.3', get_best_version(
            antlr4_atom, java, pkg_filter_uriscv_uarm64).PVR)
        self.assertEqual('4.9.3', get_best_version(
            antlr4_atom, java, pkg_filter_uriscv_arm64).PVR)
        self.assertEqual('4.9.3', get_best_version(
            antlr4_atom, java, pkg_filter_arm_uarm64).PVR)
        self.assertEqual('4.9.3', get_best_version(
            antlr4_atom, java, pkg_filter_arm_arm64).PVR)


if __name__ == '__main__':
    unittest.main()
