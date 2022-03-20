#  zarro-boogs-tools unittest Module Customization
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
import warnings


class TestCase(unittest.TestCase):
    """
    A custom drop-in replacement of unittest.TestCase designed for this
    program's tests.
    """

    def _callSetUp(self):
        self.setUp()
        # Suppress warnings due to pkgcore not seemingly closing ebuild files
        warnings.simplefilter('ignore', ResourceWarning)


main = unittest.TestProgram
