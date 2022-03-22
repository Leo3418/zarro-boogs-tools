#  Unit tests for portage.py
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
from zarro_boogs_tools.portage import *
from zarro_boogs_tools.package import get_atom_obj_from_str

import os.path


class TestPortage(unittest.TestCase):
    def test_get_accept_keywords_file_basename(self):
        """
        Test if the 'get_accept_keywords_file_basename' function returns a file
        name which, when used for a file under
        /etc/portage/package.accept_keywords, allows that file to be respected
        by Portage.
        """
        def check_visibility_to_portage(file_name: str):
            # Cannot be a file under a subdirectory
            self.assertFalse(os.path.sep in file_name)
            # Cannot be a hidden file
            self.assertFalse(file_name.startswith('.'))

        atoms = list()
        atoms.append(get_atom_obj_from_str('dev-java/antlr'))
        atoms.append(get_atom_obj_from_str('dev-java/antlr:4'))
        atoms.append(get_atom_obj_from_str('=dev-java/antlr-4.9.3'))
        atoms.append(get_atom_obj_from_str('>dev-java/antlr-4.5.3-r1'))

        for atom_obj in atoms:
            result = get_accept_keywords_file_basename(atom_obj)
            check_visibility_to_portage(result)

    def test_get_accept_keywords_contents(self):
        """
        Test if 'get_accept_keywords_contents' function returns lines to be
        added to /etc/portage/package.accept_keywords correctly based on the
        specified packages and target keyword.
        """
        # Map each new keyword to the keyword that must be accepted to install
        # the package before the new keyword is added
        keywords_dict = {
            'amd64': '~amd64',
            '~amd64': '**',
            'x86': '~x86',
            '~x86': '**'
        }

        no_pkgs = []
        for keyword in keywords_dict:
            self.assertEqual(0, len(list(
                get_accept_keywords_contents(no_pkgs, keyword))))

        jdk_cpvstr = '=virtual/jdk-11-r2'
        jdk_atom_obj = get_atom_obj_from_str(jdk_cpvstr)
        single_pkg = [jdk_atom_obj]
        for keyword in keywords_dict:
            lines = list(get_accept_keywords_contents(single_pkg, keyword))
            self.assertEqual(len(single_pkg), len(lines))
            self.assertTrue(f'{jdk_cpvstr} {keywords_dict[keyword]}' in lines)

        jre_cpvstr = '=virtual/jre-11-r2'
        jre_atom_obj = get_atom_obj_from_str(jre_cpvstr)
        multiple_pkgs = [jdk_atom_obj, jre_atom_obj]
        for keyword in keywords_dict:
            lines = list(get_accept_keywords_contents(multiple_pkgs, keyword))
            self.assertEqual(len(multiple_pkgs), len(lines))
            self.assertTrue(f'{jdk_cpvstr} {keywords_dict[keyword]}' in lines)
            self.assertTrue(f'{jre_cpvstr} {keywords_dict[keyword]}' in lines)


if __name__ == '__main__':
    unittest.main()
