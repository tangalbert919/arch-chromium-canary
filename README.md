# Chromium Canary for Arch Linux

This repository holds the files necessary to build the Canary branch for Chromium on Arch Linux. It can be installed alongside the stable version of Chromium.

## Instructions:

Run this command to install missing dependencies before building, and then the browser itself after it is successfully built:

`makepkg -si`

To use libc++ instead of libstdc++ (provided by GCC), run this command:

`FORCE_LIBCXX=yes makepkg -si`

## Credits:

* The PKGBUILD used is the modified version of this [PKGBUILD](https://git.archlinux.org/svntogit/packages.git/tree/trunk/PKGBUILD?h=packages/chromium) for the stable version of Chromium on Arch Linux.
* Some modifications were taken from this [PKGBUILD](https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=chromium-dev) for chromium-dev in the AUR.
* The `set_quilt_vars.sh` script is from the [Ungoogled Chromium](https://github.com/Eloston/ungoogled-chromium) repository.
