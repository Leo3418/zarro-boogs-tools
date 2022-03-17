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

import unittest
from zarro_boogs_tools.package import *

from pathlib import Path

import nattka.package


class TestPackage(unittest.TestCase):
    def test_get_atom_obj_from_str_pms(self):
        """
        Test if the 'get_atom_obj_from_str' function supports all kinds of
        package atoms defined by section 8.3, PMS for EAPI 8.
        """
        get_atom_obj_from_str('foo-bar/baz')

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


if __name__ == '__main__':
    unittest.main()
