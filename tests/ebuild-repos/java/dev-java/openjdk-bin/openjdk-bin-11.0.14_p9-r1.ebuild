# Copyright 1999-2022 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=8

MY_PV=${PV/_p/+}
SLOT=${MY_PV%%[.+]*}

DESCRIPTION="Prebuilt Java JDK binaries provided by Eclipse Temurin"
KEYWORDS="amd64 ~arm arm64 ppc64 ~x64-macos"
IUSE="headless-awt"
