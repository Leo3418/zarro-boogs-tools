#  zarro-boogs-tools Package Processing Functions
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

from zarro_boogs_tools.pkgcore.restriction import preprocess_restriction

from typing import Callable, Iterable, Iterator, Optional

import nattka.package
import pkgcore.ebuild.atom as atom
import pkgcore.restrictions.boolean as boolean
from pkgcore.ebuild.ebuild_src import package
from pkgcore.ebuild.errors import MalformedAtom
from pkgcore.ebuild.repository import UnconfiguredTree


def get_atom_obj_from_str(atom_str: str) -> atom:
    """
    Convert a package atom specified in string to a corresponding object.  This
    function allows fuzzy '=' version operator: it accepts any atom that
    specifies an exact version but is not started with '='.  In other words,
    both '=foo-bar/baz-1.0.2' and 'foo-bar/baz-1.0.2' are accepted by this
    function and are treated in the same way.

    :param atom_str: the string representation of the atom
    :return: the object for the atom
    :raise MalformedAtom: if the specified atom is invalid by definition of
        this function
    """

    def str_to_atom() -> atom:
        return atom.atom(atom_str, eapi='5')

    if atom_str.startswith('='):
        return str_to_atom()
    else:
        try:
            return str_to_atom()
        except MalformedAtom:
            atom_str = '=' + atom_str
            return str_to_atom()


def check_atom_obj_for_keywording(atom_obj: atom) -> Optional[str]:
    """
    Check if a package atom represented by an object is a valid atom in the
    context of keywording according to NATTkA
    <https://dev.gentoo.org/~mgorny/doc/nattka/bug.html>.  If it is, then this
    function returns 'None'; otherwise, a string describing the issue is
    returned.

    :param atom_obj: the object representing the atom
    :return: a string explaining the reason if the atom is invalid, or 'None'
        otherwise
    """
    if atom_obj is None:
        return "'None' is specified as the atom"
    if atom_obj.blocks:
        return "Atom contains a block operator"
    if atom_obj.slot_operator:
        return "Atom contains a slot operator"
    if atom_obj.use:
        return "Atom contains USE dependency"
    return None


def get_best_version(
        atom_obj: atom,
        repo: UnconfiguredTree,
        pkg_filter: Optional[Callable[[Iterator[package]], Iterable]] = None
) -> Optional[package]:
    """
    Find the best version of the package that satisfies the specified atom in
    a given ebuild repository.  If a version can be found, return the object
    that represents the best version; otherwise, 'None' is returned.

    :param atom_obj: the object representing the atom
    :param repo: the object representing the ebuild repository where candidate
        packages are searched
    :param pkg_filter: a filter for limiting the set of packages that may be
        selected as the best version; omit or specify 'None' to skip any
        filtering
    :return: the object for the best-matching package if there is one, or
        'None' otherwise
    """
    matches = repo.match(atom_obj, pkg_filter=pkg_filter)
    if len(matches) == 0:
        return None
    else:
        return nattka.package.select_best_version(matches)


def get_packages_to_process(
        main_package: package,
        target_keyword: str,
        repo: UnconfiguredTree,
        pkg_filter: Optional[Callable[[Iterator[package]], Iterable]] = None
) -> list[package]:
    """
    When keywording or stabilizing a package, find the dependencies that also
    need to be keyworded or stabilized.  All packages in the returned result
    will contain the full version specification (PVR).

    The 'target_keyword' parameter is used to specify not only the architecture
    on which the keywording or stabilization will happen but also whether the
    processing is for keywording or stabilization.  For instance, specifying
    '~amd64' as the argument for this parameter indicates that keywording is
    being performed on the amd64 architecture, whereas specifying 'amd64'
    indicates that stabilization is being done on amd64.

    'pkg_filter' can be used to restrict versions of dependencies that may be
    selected based on any attribute supported by the
    pkgcore.ebuild.ebuild_src.package class.  If the argument for this
    parameter is not omitted and is not 'None', then this function will apply
    the specified filter on every dependency when it searches for the version
    of that dependency to be included in the returned result.  If no version
    passes through the filter, then this function will search for a version of
    the dependency again without the filter.

    'pkg_filter' is never applied to 'main_package'; it is in effect only in
    dependency version selection.

    'pkg_filter' examples:
    - lambda pkgs: filter(lambda pkg: '~amd64' in pkg.keywords, pkgs)
        For each dependency, use the best version among all versions that are
        keyworded on amd64 whenever it is available.
    - lambda pkgs: filter(lambda pkg: 'amd64' in pkg.keywords, pkgs)
        For each dependency, use the best version among all versions that are
        stable on amd64 whenever it is available.

    Invocation examples:
    - To keyword dev-java/ant-core and its dependencies on riscv and avoid
      keywording dependencies that have not been stabilized on amd64 yet:
        atom = get_atom_obj_from_str('dev-java/ant-core')
        _, repo = nattka.package.find_repository(Path('/var/db/repos/gentoo'))
        target_keyword = '~riscv'
        best_version = get_best_version(atom, repo)
        packages_to_process = get_deps_to_process(
            best_version, target_keyword, repo,
            lambda pkgs: filter(lambda pkg: 'amd64' in pkg.keywords, pkgs)
        )
        # Keyword packages listed in 'packages_to_process'

    :param main_package: the main package to keyword or stabilize
    :param target_keyword: the keyword that would be added to the main
        package's 'KEYWORDS' variable after the process
    :param repo: the object representing the ebuild repository where candidate
        packages are searched
    :param pkg_filter: a filter to set a preference on the versions of
        dependencies chosen to be processed; omit or specify 'None' to skip any
        filtering
    :return: a list of the selected packages to process
    """
    # Run an ordinary breadth-first search in the package's dependency graph
    result = list()
    main_package_singleton = [main_package]
    pkg_processing_queue = list(main_package_singleton)
    visited_pkgs = set(main_package_singleton)

    while len(pkg_processing_queue) > 0:
        next_pkg = pkg_processing_queue.pop(0)
        if target_keyword in next_pkg.keywords or \
                target_keyword.lstrip('~') in next_pkg.keywords:
            # The package already has the target keyword; no action needed
            continue
        result.append(next_pkg)

        deps_restrictions = set()
        for dep_class in [next_pkg.bdepend, next_pkg.depend, next_pkg.rdepend,
                          next_pkg.pdepend, next_pkg.idepend]:
            deps_restrictions = deps_restrictions.union(dep_class.restrictions)

        processed_restrictions = set()
        for restriction in deps_restrictions:
            restriction = preprocess_restriction(restriction)
            if isinstance(restriction, atom.atom) and restriction.blocks:
                # Do not process dependencies specified as a block
                continue
            # Each dependency in an all-of group need to be processed
            # individually; if an all-of group was given to the
            # get_best_version() function directly, 'None' would be returned
            if isinstance(restriction, boolean.AndRestriction) and \
                    not isinstance(restriction, atom.atom):
                processed_restrictions = \
                    processed_restrictions.union(restriction)
            else:
                processed_restrictions.add(restriction)

        for restriction in processed_restrictions:
            dep_pkg = get_best_version(restriction, repo, pkg_filter)
            if dep_pkg is None:
                # No package matches the filter; try again without it
                dep_pkg = get_best_version(restriction, repo)
            if dep_pkg is not None and dep_pkg not in visited_pkgs:
                pkg_processing_queue.append(dep_pkg)
                visited_pkgs.add(dep_pkg)

    return result
