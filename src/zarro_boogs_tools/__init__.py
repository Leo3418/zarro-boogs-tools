#  zarro-boogs-tools Main Package Initialization File
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

__project_name__ = 'zarro-boogs-tools'
__version__ = '0.0.2'

"""
An abbreviation of this project's name that may be used in names of files
pertaining to this program to help users avoid having to frequently type in the
entire project name.
"""
__project_name_abbrev__ = ''.join(map(
    lambda part: part[0], __project_name__.split('-')))
