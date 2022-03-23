#  Unit tests for list.py
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
from zarro_boogs_tools.list import *
from zarro_boogs_tools.package import get_atom_obj_from_str, get_best_version

import os.path
from pathlib import Path

import nattka.package


class TestList(unittest.TestCase):
    java = None
    profile = None

    @classmethod
    def setUpClass(cls):
        _, java = nattka.package.find_repository(
            Path('tests/ebuild-repos/java'))
        profile = OnDiskProfile(os.path.join(java.base, 'profiles'), 'base')
        cls.java = java
        cls.profile = profile

    def test_generate_package_lists_empty_packages(self):
        """
        Test the 'generate_package_lists' function when no packages are
        specified for keywording or stabilization.
        """
        keyword_dict = get_package_lists(self.java, [], self.profile, '~amd64')
        stable_dict = get_package_lists(self.java, [], self.profile, 'amd64')
        self.assertEqual(0, len(keyword_dict))
        self.assertEqual(0, len(stable_dict))

    def test_generate_package_lists_simple_keyword(self):
        """
        Test the 'generate_package_lists' function for a simple keywording
        task involving only a single package.
        """
        openjdk_bin11 = get_best_version(
            get_atom_obj_from_str('dev-java/openjdk-bin:11'), self.java)
        pkg_to_list_dict = get_package_lists(
            self.java, [openjdk_bin11], self.profile, '~riscv')
        self.assertEqual(1, len(pkg_to_list_dict))
        openjdk_bin11_pkgs = pkg_to_list_dict[openjdk_bin11]
        self.assertEqual(1, len(openjdk_bin11_pkgs))
        self.assertEqual(openjdk_bin11, openjdk_bin11_pkgs[0])

    def test_generate_package_lists_simple_stable(self):
        """
        Test the 'generate_package_lists' function for a simple stabilization
        task involving only a single package.
        """
        musl = get_best_version(
            get_atom_obj_from_str('sys-libs/musl'), self.java)
        pkg_to_list_dict = get_package_lists(
            self.java, [musl], self.profile, 'amd64')
        self.assertEqual(1, len(pkg_to_list_dict))
        musl_pkgs = pkg_to_list_dict[musl]
        self.assertEqual(1, len(musl_pkgs))
        self.assertEqual(musl, musl_pkgs[0])

    def test_generate_package_lists_multiple_stable(self):
        """
        Test the 'generate_package_lists' function for a stabilization task
        involving multiple packages.
        """
        ant_core = get_best_version(
            get_atom_obj_from_str('dev-java/ant-core'), self.java)
        c3p0 = get_best_version(
            get_atom_obj_from_str('dev-java/c3p0'), self.java)
        pkg_to_list_dict = get_package_lists(
            self.java, [ant_core, c3p0], self.profile, 'amd64')
        self.assertEqual(2, len(pkg_to_list_dict))
        ant_core_pkgs = pkg_to_list_dict[ant_core]
        self.assertEqual(1, len(ant_core_pkgs))
        self.assertEqual(ant_core, ant_core_pkgs[0])
        c3p0_pkgs = pkg_to_list_dict[c3p0]
        self.assertEqual(1, len(c3p0_pkgs))
        self.assertEqual(c3p0, c3p0_pkgs[0])
