# Copyright 1999-2022 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=7

SLOT="${PV%%[.+]*}"

DESCRIPTION="Open source implementation of the Java programming language"
KEYWORDS="amd64 arm64 ppc64 x86"
IUSE="headless-awt selinux"

RDEPEND="
	selinux? ( sec-policy/selinux-java )
"

DEPEND="
	|| (
		dev-java/openjdk-bin:${SLOT}
		dev-java/icedtea-bin:${SLOT}
		dev-java/openjdk:${SLOT}
		dev-java/icedtea:${SLOT}
	)
"
