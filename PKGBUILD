# Maintainer: Evangelos Foutras <evangelos@foutrelis.com>
# Contributor: Pierre Schmitz <pierre@archlinux.de>
# Contributor: Jan "heftig" Steffens <jan.steffens@gmail.com>
# Contributor: Daniel J Griffiths <ghost1227@archlinux.us>

pkgname=chromium-canary
pkgver=81.0.4040.5
pkgrel=1
_launcher_ver=6
pkgdesc="A web browser built for speed, simplicity, and security"
arch=('x86_64')
url="https://www.chromium.org/Home"
license=('BSD')
depends=('gtk3' 'nss' 'alsa-lib' 'xdg-utils' 'libxss' 'libcups' 'libgcrypt'
         'ttf-font' 'systemd' 'dbus' 'libpulse' 'pciutils' 'json-glib'
         'desktop-file-utils' 'hicolor-icon-theme')
makedepends=('python' 'python2' 'gperf' 'yasm' 'mesa' 'ninja' 'nodejs' 'git'
             'pipewire' 'clang' 'lld' 'gn' 'java-runtime-headless')
optdepends=('pepper-flash: support for Flash content'
            'pipewire: WebRTC desktop sharing under Wayland'
            'kdialog: needed for file dialogs in KDE'
            'org.freedesktop.secrets: password storage backend on GNOME / Xfce'
            'kwallet: for storing passwords in KWallet on KDE desktops')
install=chromium.install
source=(https://commondatastorage.googleapis.com/chromium-browser-official/chromium-$pkgver.tar.xz
        chromium-launcher-$_launcher_ver.tar.gz::https://github.com/foutrelis/chromium-launcher/archive/v$_launcher_ver.tar.gz
        chromium-system-zlib.patch
        fix-spammy-unique-font-matching-log.patch
        chromium-widevine.patch
        chromium-skia-harmony.patch
        chromium-unbundle-libxml.patch
        chromium-include-vector.patch
        default-constructor-error.patch)
sha256sums=("$(curl -sL https://commondatastorage.googleapis.com/chromium-browser-official/chromium-${pkgver}.tar.xz.hashes | grep sha256 | cut -d ' ' -f3)"
            '04917e3cd4307d8e31bfb0027a5dce6d086edb10ff8a716024fbb8bb0c7dccf1'
            'ae292e27e2be927180a0c7b9fffafd44bb915d88e4c5b31ad1e5fd4f700d875d'
            'c628b810f79510042e46533d6c87257b0c80f8a3acdb4be730228316d6b00439'
            '7411a7df3522938d66b0cd4be7c0e5b45d02daff2548efe63b09e665b552aae9'
            '27debc7fb7f64415c1b7747c76ae93ade95db2beb84aa319df21bc0d0cdfb6e2'
            '94e735f4cdeb197ea6b74a80109e51965ca9ed89612e52e179ce5946c3d52f5c'
            '1483a0dd74a2b2a2846c031fce3ace52818b53a9e853ac10370442a6a7c63b88'
            'd459deb0611e961ce2e1282e9381f95836fc01070e773d93fc97337d082c3b6e')

# Possible replacements are listed in build/linux/unbundle/replace_gn_files.py
# Keys are the names in the above script; values are the dependencies in Arch
declare -gA _system_libs=(
  [ffmpeg]=ffmpeg
  [flac]=flac
  [fontconfig]=fontconfig
  [freetype]=freetype2
  [harfbuzz-ng]=harfbuzz
  [icu]=icu
  [libdrm]=
  [libjpeg]=libjpeg
  #[libpng]=libpng    # https://crbug.com/752403#c10
  [libvpx]=libvpx
  [libwebp]=libwebp
  [libxml]=libxml2
  [libxslt]=libxslt
  [opus]=opus
  [re2]=re2
  [snappy]=snappy
  [yasm]=
  [zlib]=minizip
)
_unwanted_bundled_libs=(
  ${!_system_libs[@]}
  ${_system_libs[libjpeg]+libjpeg_turbo}
)
depends+=(${_system_libs[@]})

# Google API keys (see https://www.chromium.org/developers/how-tos/api-keys)
# Note: These are for Arch Linux use ONLY. For your own distribution, please
# get your own set of keys.
_google_api_key=apikey
_google_default_client_id=noid
_google_default_client_secret=nosecret

prepare() {
  cd "$srcdir/chromium-$pkgver"

  # Allow building against system libraries in official builds
  sed -i 's/OFFICIAL_BUILD/GOOGLE_CHROME_BUILD/' \
    tools/generate_shim_headers/generate_shim_headers.py

  # https://crbug.com/893950
  sed -i -e 's/\<xmlMalloc\>/malloc/' -e 's/\<xmlFree\>/free/' \
    third_party/blink/renderer/core/xml/*.cc \
    third_party/blink/renderer/core/xml/parser/xml_document_parser.cc \
    third_party/libxml/chromium/libxml_utils.cc

  # Fixes from Gentoo
  patch -Np1 -i ../chromium-system-zlib.patch
  patch -Np1 -i ../chromium-unbundle-libxml.patch

  # https://crbug.com/1005508
  patch -Np1 -i ../fix-spammy-unique-font-matching-log.patch

  # Load bundled Widevine CDM if available (see chromium-widevine in the AUR)
  # M79 is supposed to download it as a component but it doesn't seem to work
  patch -Np1 -i ../chromium-widevine.patch

  # https://crbug.com/skia/6663#c10
  patch -Np1 -i ../chromium-skia-harmony.patch

  # Custom fixes
  patch -Np1 -i ../chromium-include-vector.patch
  patch -Np1 -i ../default-constructor-error.patch

  # Force script incompatible with Python 3 to use /usr/bin/python2
  sed -i '1s|python$|&2|' third_party/dom_distiller_js/protoc_plugins/*.py

  mkdir -p third_party/node/linux/node-linux-x64/bin
  ln -sf /usr/bin/node third_party/node/linux/node-linux-x64/bin/

  # Remove bundled libraries for which we will use the system copies; this
  # *should* do what the remove_bundled_libraries.py script does, with the
  # added benefit of not having to list all the remaining libraries
  local _lib
  for _lib in ${_unwanted_bundled_libs[@]}; do
    find "third_party/$_lib" -type f \
      \! -path "third_party/$_lib/chromium/*" \
      \! -path "third_party/$_lib/google/*" \
      \! -path 'third_party/yasm/run_yasm.py' \
      \! -regex '.*\.\(gn\|gni\|isolate\)' \
      -delete
  done

  python2 build/linux/unbundle/replace_gn_files.py \
    --system-libraries "${!_system_libs[@]}"

  # Use chromium-canary as brand name. Modified from chromium-dev PKGBUILD in the AUR.
  sed -e 's|=Chromium|&-canary|g' \
      -i chrome/app/theme/chromium/BRANDING
  sed -e '0,/output_name = "chrome"/s/= "chrome"/= "chromium-canary"/' \
      -e 's|root_out_dir/chrome"|root_out_dir/chromium-canary"|g' \
      -i chrome/BUILD.gn
  sed -e 's|"chromium-browser"|"chromium-canary"|g' \
      -i media/audio/pulse/pulse_util.cc
  sed -e 's|"Chromium|&-canary|g' \
      -i chrome/common/chrome_constants.cc
  sed -e 's|chromium-browser|chromium-canary|g' \
      -i chrome/browser/shell_integration_linux.cc \
      -i chrome/browser/ui/gtk/gtk_util.cc
  sed -e 's|chromium|&-canary|' \
      -i chrome/common/chrome_paths_linux.cc
  sed -e 's|/etc/chromium|&-canary|' \
      -e 's|/usr/share/chromium|&-canary|' \
      -i chrome/common/chrome_paths.cc
  sed -e 's|/etc/chromium|&-canary|' \
      -e "s|'app_name': 'Chromium|&-canary|g" \
      -i components/policy/tools/template_writers/writer_configuration.py
}

build() {
  make -C chromium-launcher-$_launcher_ver CHROMIUM_SUFFIX="-canary"

  cd "$srcdir/chromium-$pkgver"

  if check_buildoption ccache y; then
    # Avoid falling back to preprocessor mode when sources contain time macros
    export CCACHE_SLOPPINESS=time_macros
  fi

  export CC=clang
  export CXX=clang++
  export AR=ar
  export NM=nm

  local _flags=(
    'custom_toolchain="//build/toolchain/linux/unbundle:default"'
    'host_toolchain="//build/toolchain/linux/unbundle:default"'
    'clang_use_chrome_plugins=false'
    'is_official_build=true' # implies is_cfi=true on x86_64
    'treat_warnings_as_errors=false'
    'fieldtrial_testing_like_official_build=true'
    'ffmpeg_branding="Chrome"'
    'proprietary_codecs=true'
    'rtc_use_pipewire=true'
    'link_pulseaudio=true'
    'use_gnome_keyring=false'
    'use_sysroot=false'
    'linux_use_bundled_binutils=false'
    'use_custom_libcxx=false'
    'enable_hangout_services_extension=true'
    'enable_widevine=true'
    'enable_nacl=false'
    'enable_swiftshader=false'
    "google_api_key=\"${_google_api_key}\""
    "google_default_client_id=\"${_google_default_client_id}\""
    "google_default_client_secret=\"${_google_default_client_secret}\""
  )

  if [[ -n ${_system_libs[icu]+set} ]]; then
    _flags+=('icu_use_data_file=false')
  fi

  if check_option strip y; then
    _flags+=('symbol_level=0')
  fi

  # Facilitate deterministic builds (taken from build/config/compiler/BUILD.gn)
  CFLAGS+='   -Wno-builtin-macro-redefined'
  CXXFLAGS+=' -Wno-builtin-macro-redefined'
  CPPFLAGS+=' -D__DATE__=  -D__TIME__=  -D__TIMESTAMP__='

  # Do not warn about unknown warning options
  CFLAGS+='   -Wno-unknown-warning-option'
  CXXFLAGS+=' -Wno-unknown-warning-option'

  gn gen out/Release --args="${_flags[*]}" --script-executable=/usr/bin/python2
  ninja -C out/Release chrome chrome_sandbox chromedriver
}

package() {
  cd chromium-launcher-$_launcher_ver
  make PREFIX=/usr DESTDIR="$pkgdir" CHROMIUM_SUFFIX="-canary" install
  install -Dm644 LICENSE \
    "$pkgdir/usr/share/licenses/chromium-canary/LICENSE.launcher"

  cd "$srcdir/chromium-$pkgver"

  # Install binaries
  install -D out/Release/chromium-canary "$pkgdir/usr/lib/chromium-canary/chromium-canary"
  install -Dm4755 out/Release/chrome_sandbox "$pkgdir/usr/lib/chromium-canary/chrome-sandbox"
  install -D out/Release/crashpad_handler "$pkgdir/usr/lib/chromium-canary/crashpad_handler"
  ln -sf /usr/lib/chromium-canary/chromedriver "$pkgdir/usr/bin/chromedriver-canary"

  # Install .desktop and manpages.
  install -Dm644 chrome/installer/linux/common/desktop.template \
    "$pkgdir/usr/share/applications/chromium-canary.desktop"
  install -Dm644 chrome/app/resources/manpage.1.in \
    "$pkgdir/usr/share/man/man1/chromium-canary.1"
  sed -i \
    -e "s/@@MENUNAME@@/Chromium Canary/g" \
    -e "s/@@PACKAGE@@/chromium-canary/g" \
    -e "s/@@PROGNAME@@/chromium-canary/g" \
    -e "s/@@USR_BIN_SYMLINK_NAME@@/chromium-canary/g" \
    "$pkgdir/usr/share/applications/chromium-canary.desktop" \
    "$pkgdir/usr/share/man/man1/chromium-canary.1"

  # Install resources and locales.
  cp \
    out/Release/{chrome_{100,200}_percent,resources}.pak \
    out/Release/{*.bin,chromedriver} \
    "$pkgdir/usr/lib/chromium-canary/"
  install -Dm644 -t "$pkgdir/usr/lib/chromium-canary/locales" out/Release/locales/*.pak

  if [[ -z ${_system_libs[icu]+set} ]]; then
    cp out/Release/icudtl.dat "$pkgdir/usr/lib/chromium-canary/"
  fi

  # Install icons.
  for size in 24 48 64 128 256; do
    install -Dm644 "chrome/app/theme/chromium/product_logo_$size.png" \
      "$pkgdir/usr/share/icons/hicolor/${size}x${size}/apps/chromium-canary.png"
  done

  for size in 16 32; do
    install -Dm644 "chrome/app/theme/default_100_percent/chromium/product_logo_$size.png" \
      "$pkgdir/usr/share/icons/hicolor/${size}x${size}/apps/chromium-canary.png"
  done

  # Install license.
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/chromium-canary/LICENSE"
}

# vim:set ts=2 sw=2 et:
