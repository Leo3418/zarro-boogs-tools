# Copyright 1999-2021 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=7

DESCRIPTION="Simple and Fast Multimedia Library (SFML)"
SLOT="0/$(ver_cut 1-2)"
KEYWORDS="amd64 ~arm64 ~riscv x86"
IUSE="doc"

RDEPEND="
	media-libs/libogg
"
DEPEND="${RDEPEND}"
BDEPEND="
	doc? ( app-doc/doxygen )
"
