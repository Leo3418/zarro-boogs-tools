# Copyright 1999-2022 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=8

DESCRIPTION="High speed arctic racing game based on Tux Racer"
SLOT="0"
KEYWORDS="~amd64"
IUSE="vanilla"

RDEPEND="
	media-libs/libsfml:0=
"
DEPEND="${RDEPEND}"
BDEPEND="
	virtual/pkgconfig
	!vanilla? (
		media-sound/modplugtools
		media-sound/sox[ogg]
	)
"
