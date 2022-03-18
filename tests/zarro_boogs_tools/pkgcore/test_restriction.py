#  Unit tests for pkgcore/restriction.py
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
from zarro_boogs_tools.pkgcore.restriction import *

from pathlib import Path
from typing import Optional

import nattka.package
import pkgcore.ebuild.atom as atom
import pkgcore.restrictions.boolean as boolean
import pkgcore.restrictions.restriction as restriction


# noinspection PyTypeChecker
class TestRestriction(unittest.TestCase):
    @staticmethod
    def find_first_use_conditional(dep_class) -> Optional[restriction.base]:
        for restrict in dep_class.restrictions:
            if isinstance(restrict, Conditional):
                return restrict
        return None

    def setUp(self):
        _, etr_simplified = nattka.package.find_repository(
            Path('tests/ebuild-repos/etr-simplified'))
        self.etr_simplified = etr_simplified
        _, java = nattka.package.find_repository(
            Path('tests/ebuild-repos/java'))
        self.java = java

        self.etr = get_best_version(
            get_atom_obj_from_str('games-action/extreme-tuxracer'),
            self.etr_simplified
        )
        self.etr_use_cond = self.find_first_use_conditional(self.etr.bdepend)

    def test_preprocess_restriction(self):
        """
        Test if the 'preprocess_restriction' function can correctly unwrap a
        USE-conditional group and strip USE dependencies at the same time.
        """
        etr_use_cond_preprocessed = preprocess_restriction(self.etr_use_cond)
        self.assertIsInstance(
            etr_use_cond_preprocessed, boolean.AndRestriction)
        self.assertEqual(2, len(etr_use_cond_preprocessed))
        etr_use_cond_strs = [a.__str__() for a in
                             etr_use_cond_preprocessed]
        self.assertTrue('media-sound/modplugtools' in etr_use_cond_strs)
        self.assertTrue('media-sound/sox' in etr_use_cond_strs)

    def test_unwrap_use_conditional(self):
        """
        Test if the 'unwrap_use_conditional' function can correctly unwrap a
        USE-conditional group while it keeps other types of dependency
        specification intact.
        """
        etr_use_cond_unwrapped = unwrap_use_conditional(self.etr_use_cond)
        self.assertIsInstance(
            etr_use_cond_unwrapped, boolean.AndRestriction)
        self.assertEqual(2, len(etr_use_cond_unwrapped))
        etr_use_cond_strs = [a.__str__() for a in etr_use_cond_unwrapped]
        self.assertTrue('media-sound/modplugtools' in etr_use_cond_strs)
        self.assertTrue('media-sound/sox[ogg]' in etr_use_cond_strs)

        libsfml = get_best_version(
            get_atom_obj_from_str('media-libs/libsfml'),
            self.etr_simplified
        )
        libsfml_use_cond = self.find_first_use_conditional(libsfml.bdepend)
        libsfml_use_cond_unwrapped = unwrap_use_conditional(libsfml_use_cond)
        self.assertIsInstance(
            libsfml_use_cond_unwrapped, boolean.AndRestriction)
        self.assertEqual(1, len(libsfml_use_cond_unwrapped))
        libsfml_use_cond_strs = [a.__str__() for a in
                                 libsfml_use_cond_unwrapped]
        self.assertTrue('app-doc/doxygen' in libsfml_use_cond_strs)

        sox = get_best_version(
            get_atom_obj_from_str('media-sound/sox'),
            self.etr_simplified
        )
        sox_use_cond = self.find_first_use_conditional(sox.rdepend)
        sox_use_cond_unwrapped = unwrap_use_conditional(sox_use_cond)
        self.assertIsInstance(sox_use_cond_unwrapped, boolean.AndRestriction)
        self.assertEqual(1, len(sox_use_cond_unwrapped))
        sox_use_cond_strs = [a.__str__() for a in sox_use_cond_unwrapped]
        self.assertTrue('media-libs/libogg' in sox_use_cond_strs)

        etr_normal_restrict = self.etr.rdepend[0]
        etr_normal_restrict_unwrapped = \
            unwrap_use_conditional(etr_normal_restrict)
        self.assertIsInstance(etr_normal_restrict_unwrapped, atom.atom)
        self.assertEqual('media-libs/libsfml:0=',
                         etr_normal_restrict_unwrapped.__str__())

    def test_strip_use_dep_from_restriction(self):
        """
        Test if the 'strip_use_dep_from_restriction' function can correctly
        strip any USE dependency from a restriction of a supported type and
        keep restrictions without a USE dependency intact.
        """
        pkgconfig = get_best_version(
            get_atom_obj_from_str('virtual/pkgconfig'),
            self.etr_simplified
        )
        pkgconfig_use_dep = pkgconfig.rdepend[0]
        pkgconfig_use_dep_stripped = \
            strip_use_dep_from_restriction(pkgconfig_use_dep)
        self.assertIsInstance(pkgconfig_use_dep_stripped, atom.atom)
        self.assertEqual('>=dev-util/pkgconf-1.3.7',
                         pkgconfig_use_dep_stripped.__str__())

        jdk = get_best_version(get_atom_obj_from_str('virtual/jdk'), self.java)
        jdk_use_dep = jdk.rdepend[0]
        jdk_use_dep_stripped = strip_use_dep_from_restriction(jdk_use_dep)
        self.assertIsInstance(jdk_use_dep_stripped, boolean.OrRestriction)
        self.assertEqual(2, len(jdk_use_dep_stripped))
        jdk_use_dep_strs = [a.__str__() for a in jdk_use_dep_stripped]
        self.assertTrue('dev-java/openjdk-bin:17' in jdk_use_dep_strs)
        self.assertTrue('dev-java/openjdk:17' in jdk_use_dep_strs)

        openjdk8 = get_best_version(
            get_atom_obj_from_str('dev-java/openjdk:8'),
            self.java
        )
        openjdk8_use_dep = openjdk8.depend[0]
        openjdk8_use_dep_stripped = \
            strip_use_dep_from_restriction(openjdk8_use_dep)
        self.assertIsInstance(openjdk8_use_dep_stripped, boolean.OrRestriction)
        self.assertEqual(4, len(openjdk8_use_dep_stripped))
        openjdk8_use_dep_strs = [a.__str__() for a in openjdk8_use_dep_stripped]
        self.assertTrue('dev-java/openjdk-bin:8' in openjdk8_use_dep_strs)
        self.assertTrue('dev-java/icedtea-bin:8' in openjdk8_use_dep_strs)
        self.assertTrue('dev-java/openjdk:8' in openjdk8_use_dep_strs)
        self.assertTrue('dev-java/icedtea:8' in openjdk8_use_dep_strs)

        # AndRestriction is covered by test_preprocess_restriction


if __name__ == '__main__':
    unittest.main()
