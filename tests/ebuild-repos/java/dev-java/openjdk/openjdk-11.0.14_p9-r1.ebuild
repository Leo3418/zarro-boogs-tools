# Copyright 1999-2022 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=7

MY_PV="${PV%_p*}-ga"
SLOT="${MY_PV%%[.+]*}"

DESCRIPTION="Open source implementation of the Java programming language"
KEYWORDS="amd64 ~arm arm64 ppc64 ~x86"
IUSE="headless-awt system-bootstrap"

DEPEND="
	system-bootstrap? (
		|| (
			dev-java/openjdk-bin:${SLOT}
			dev-java/openjdk:${SLOT}
		)
	)
"
