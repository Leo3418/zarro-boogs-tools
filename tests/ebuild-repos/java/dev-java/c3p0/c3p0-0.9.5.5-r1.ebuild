# Copyright 1999-2022 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=8

DESCRIPTION="JDBC drivers with JNDI-bindable DataSources"

SLOT="0"
KEYWORDS="~amd64 ~ppc64 ~x86 ~amd64-linux ~x86-linux"

DEPEND="
	>=virtual/jdk-1.8:*
	dev-java/ant-core:0
"

RDEPEND="
	>=virtual/jre-1.8:*
"
