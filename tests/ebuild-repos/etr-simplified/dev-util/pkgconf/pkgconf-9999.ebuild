# Copyright 2012-2021 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=7

if [[ ${PV} == "9999" ]] ; then
	PROPERTIES="live"
else
	KEYWORDS="~alpha ~amd64 ~arm ~arm64 ~hppa ~ia64 ~m68k ~mips ~ppc ~ppc64 ~riscv ~s390 ~sparc ~x86 ~x64-cygwin ~ppc-macos ~x64-macos"
fi

DESCRIPTION="pkg-config compatible replacement with no dependencies other than ANSI C89"
SLOT="0/3"

RDEPEND="
	!dev-util/pkgconfig
"
