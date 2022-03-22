#  Unit tests for inference.py
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
from zarro_boogs_tools.inference import *
from zarro_boogs_tools.package import get_atom_obj_from_str, get_best_version

from pathlib import Path

import nattka.package


class TestInference(unittest.TestCase):
    def test_is_stabilizing(self):
        """
        Test if the 'is_stabilizing' function correctly infers the type of
        keyword change requested based on keywords of specified packages on
        specified architectures.
        """
        _, java = nattka.package.find_repository(
            Path('tests/ebuild-repos/java'))

        musl = get_best_version(
            get_atom_obj_from_str('=sys-libs/musl-1.2.2-r7'), java)
        musl_singleton = [musl]
        musl_stable_arches = ['amd64', 'x86']
        musl_unstable_arches = ['mips']
        musl_unkeyworded_arches = ['riscv']
        musl_keyworded_arches = musl_stable_arches + musl_unstable_arches
        musl_mixed_arches = musl_keyworded_arches + musl_unkeyworded_arches
        self.assertTrue(
            is_stabilizing(musl_singleton, musl_stable_arches))
        self.assertTrue(
            is_stabilizing(musl_singleton, musl_unstable_arches))
        self.assertFalse(
            is_stabilizing(musl_singleton, musl_unkeyworded_arches))
        self.assertTrue(
            is_stabilizing(musl_singleton, musl_keyworded_arches))
        self.assertFalse(
            is_stabilizing(musl_singleton, musl_mixed_arches))

        glibc = get_best_version(
            get_atom_obj_from_str('=sys-libs/glibc-2.33-r13'), java)
        libcs = [glibc, musl]
        libcs_stable_arches = ['amd64']
        libcs_mixed_stable_arches = ['ppc64']
        libcs_unstable_arches = ['mips']
        libcs_all_keyworded_arches = \
            libcs_stable_arches + libcs_mixed_stable_arches + \
            libcs_unstable_arches
        libcs_some_unkeyworded_arches = ['riscv']
        libcs_mixed_args = \
            libcs_all_keyworded_arches + libcs_some_unkeyworded_arches
        libcs_unkeyworded_arches = ['s360']
        libcs_all_arches = libcs_mixed_args + libcs_unkeyworded_arches
        self.assertTrue(is_stabilizing(libcs, libcs_stable_arches))
        self.assertTrue(is_stabilizing(libcs, libcs_mixed_stable_arches))
        self.assertTrue(is_stabilizing(libcs, libcs_unstable_arches))
        self.assertTrue(is_stabilizing(libcs, libcs_all_keyworded_arches))
        self.assertFalse(is_stabilizing(libcs, libcs_some_unkeyworded_arches))
        self.assertFalse(is_stabilizing(libcs, libcs_mixed_args))
        self.assertFalse(is_stabilizing(libcs, libcs_unkeyworded_arches))
        self.assertFalse(is_stabilizing(libcs, libcs_all_arches))


if __name__ == '__main__':
    unittest.main()
