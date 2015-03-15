#!/bin/bash

startdir="$PWD"

set -e
pkgname=tisean
pkgver=3.0.1
pkgrel=1
pkgdir="$PWD"/pkgdir
sourcefile=TISEAN_"$pkgver".tar.gz
sha256sum=cd6662505a2e411218f5d34ccb8bf206a6148b6c79b1cc8e4fa4dc11dfd00534
arch=amd64; [[ $(uname -m) = i*86 ]] && arch=i386

makedeps=(build-essential fort77)

pkgdir="$startdir/pkg"
rm -fr "$pkgdir"
mkdir -p "$pkgdir"

get() {
	cd "$startdir"
	if [[ ! -e $sourcefile ]]; then
		curl -O http://www.mpipks-dresden.mpg.de/~tisean/"$sourcefile"
	fi
	printf "%s %s\n" "$sha256sum" "$sourcefile" | sha256sum -c
	rm -fr Tisean_"$pkgver"
	tar -xzf "$sourcefile"
}

build() {
	cd "$startdir"/Tisean_"$pkgver"
	./configure --prefix="$pkgdir"/usr --bindir=/lib/"$pkgname"
	make
}

package() {
	cd "$startdir"/Tisean_"$pkgver"
	mkdir -p "$pkgdir"/usr/lib/"$pkgname" "$pkgdir"/usr/share/doc/"$pkgname"
	make PATH="$pkgdir"/usr/lib/"$pkgname":"$PATH" install
	cp -r docs/* examples "$pkgdir"/usr/share/doc/"$pkgname"

	mkdir -p "$pkgdir"/etc/profile.d
	cat <<-EOF > "$pkgdir"/etc/profile.d/"$pkgname".sh
		tisean() {
			export PATH="/usr/lib/$pkgname":"$PATH"
		}
		EOF
}

deb() {
	mkdir "$pkgdir"/DEBIAN
	cd "$pkgdir"/DEBIAN

	cat <<-EOF > control
		Package: $pkgname
		Version: $pkgver-$pkgrel
		Section: extra
		Priority: optional
		Architecture: $arch
		Maintainer: Matt Monaco <matthew.monaco@colorado.edu>
		Description: Nonlinear time series routines
		EOF

	cd "$startdir"
	dpkg-deb -b "$pkgdir" "$pkgname-$pkgver-${pkgrel}_$arch.deb"
}

get
build
package
deb
