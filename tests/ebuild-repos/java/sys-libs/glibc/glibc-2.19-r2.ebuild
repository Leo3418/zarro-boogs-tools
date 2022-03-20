# Copyright 1999-2021 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=6

DESCRIPTION="GNU libc C library"
SLOT="2.2"

if [[ ${PV} == 9999* ]]; then
	PROPERTIES="live"
else
	KEYWORDS="~amd64"
fi
