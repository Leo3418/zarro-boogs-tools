#!/usr/bin/env bash

# pip-vcs-install-as-needed.sh: Install pip packages from VCS as needed.
#
# Copyright (C) 2022 Yuan Liao
# Copyright (C) 2022 zarro-boogs-tools Contributors
#
# This file is part of zarro-boogs-tools.
#
# zarro-boogs-tools is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# zarro-boogs-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with zarro-boogs-tools.  If not, see
# <https://www.gnu.org/licenses/>.

usage() {
    local output_fd="${1:-2}"

    local help="\
Usage: ${0} VCS_URL_WITH_EGG...
If the egg specified in a VCS_URL_WITH_EGG is not installed, use pip to
install it; otherwise, skip pip invocation for it.

A valid VCS_URL_WITH_EGG might look like:
    git+https://git.example.com/my-project.git@v1.0#egg=my-project==1.0

Although pip supports package installation from a VCS URL, it might
fetch from the VCS even if the specified package is already installed,
which wastes resources and prevents offline work.  This script avoids
invoking pip at all if the package that would be installed from a
VCS_URL_WITH_EGG is already present.

For more information, please consult pip's documentation:
https://pip.pypa.io/en/stable/topics/vcs-support/"

    echo "${help}" >&"${output_fd}"
}

main() {
    if [[ "${#}" -lt 1 ]]; then
        usage 2
        return 2
    fi

    local egg
    while [[ "${#}" -gt 0 ]]; do
        egg="$(cut -d = -f 2- <<< "${1}")"

        # 'grep -q' may cause grep to exit before pip,
        # resulting in BrokenPipeError
        if pip list -l --format freeze | grep -w "${egg}" > /dev/null; then
            echo "Skipping installed package: ${egg}"
        else
            echo "Installing package via pip: ${egg}"
            pip install "${1}"
        fi

        shift
    done

    return
}

main "${@}"
