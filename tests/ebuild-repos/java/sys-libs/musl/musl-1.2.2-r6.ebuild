# Copyright 1999-2022 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=7

if [[ ${PV} == "9999" ]] ; then
	PROPERTIES="live"
else
	KEYWORDS="-* amd64 arm arm64 ~mips ppc ppc64 x86"
fi

DESCRIPTION="Light, fast and simple C library focused on standards-conformance and safety"
SLOT="0"
