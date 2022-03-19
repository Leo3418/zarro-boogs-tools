# Copyright 2022 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=8

DESCRIPTION="Consumer whose pkg-* USE flags should be restricted individually"
SLOT="0"
KEYWORDS="~amd64"
IUSE="force mask normal pkg-force pkg-mask pkg-stable-force pkg-stable-mask stable-force stable-mask"

RDEPEND="
	force?				( dev-libs/force )
	mask?				( dev-libs/mask )
	normal?				( dev-libs/normal )
	pkg-force?			( dev-libs/pkg-force )
	pkg-mask?			( dev-libs/pkg-mask )
	pkg-stable-force?	( dev-libs/pkg-stable-force )
	pkg-stable-mask?	( dev-libs/pkg-stable-mask )
	stable-force?		( dev-libs/stable-force )
	stable-mask?		( dev-libs/stable-mask )
"

DEPEND="
	${RDEPEND}
"
