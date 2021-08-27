# Maintainer: Evangelos Foutras <evangelos@foutrelis.com>
# Contributor: Pierre Schmitz <pierre@archlinux.de>
# Contributor: Jan "heftig" Steffens <jan.steffens@gmail.com>
# Contributor: Daniel J Griffiths <ghost1227@archlinux.us>

pkgname=chromium-canary
pkgver=94.0.4606.5
pkgrel=1
_launcher_ver=7
_gcc_patchset=3
pkgdesc="A web browser built for speed, simplicity, and security"
arch=('x86_64')
url="https://www.chromium.org/Home"
license=('BSD')
depends=('gtk3' 'nss' 'alsa-lib' 'xdg-utils' 'libxss' 'libcups' 'libgcrypt'
         'ttf-liberation' 'systemd' 'dbus' 'libpulse' 'pciutils' 'libva'
         'desktop-file-utils' 'hicolor-icon-theme')
makedepends=('python' 'python2' 'gperf' 'ninja' 'nodejs' 'git'
             'pipewire' 'clang' 'lld' 'gn' 'java-runtime-headless'
             'python2-setuptools')
optdepends=('pipewire: WebRTC desktop sharing under Wayland'
            'kdialog: needed for file dialogs in KDE'
            'org.freedesktop.secrets: password storage backend on GNOME / Xfce'
            'kwallet: for storing passwords in KWallet on KDE desktops')
install=chromium.install
source=(https://commondatastorage.googleapis.com/chromium-browser-official/chromium-$pkgver.tar.xz
        chromium-launcher-$_launcher_ver.tar.gz::https://github.com/foutrelis/chromium-launcher/archive/v$_launcher_ver.tar.gz
        https://github.com/stha09/chromium-patches/releases/download/chromium-${pkgver%%.*}-patchset-$_gcc_patchset/chromium-${pkgver%%.*}-patchset-$_gcc_patchset.tar.xz
        chromium-94-sql-assert.patch)
sha256sums=("$(curl -sL https://commondatastorage.googleapis.com/chromium-browser-official/chromium-${pkgver}.tar.xz.hashes | grep sha256 | cut -d ' ' -f3)"
            '86859c11cfc8ba106a3826479c0bc759324a62150b271dd35d1a0f96e890f52f'
            '22692bddaf2761c6ddf9ff0bc4722972bca4d4c5b2fd3e5dbdac7eb60d914320'
            '5cc09865a4b08d4f56042cc9897ed0dec7320b3e10f2b20ae8f147c0a6cdf953')

# Possible replacements are listed in build/linux/unbundle/replace_gn_files.py
# Keys are the names in the above script; values are the dependencies in Arch
declare -gA _system_libs=(
  #[ffmpeg]=ffmpeg
  [flac]=flac
  [fontconfig]=fontconfig
  [freetype]=freetype2
  [harfbuzz-ng]=harfbuzz
  [icu]=icu
  [libdrm]=
  [libjpeg]=libjpeg
  [libpng]=libpng
  #[libvpx]=libvpx
  [libwebp]=libwebp
  [libxml]=libxml2
  [libxslt]=libxslt
  [opus]=opus
  [re2]=re2
  [snappy]=snappy
  [zlib]=minizip
)
_unwanted_bundled_libs=(
  $(printf "%s\n" ${!_system_libs[@]} | sed 's/^libjpeg$/&_turbo/')
)
depends+=(${_system_libs[@]})

# Google API keys (see https://www.chromium.org/developers/how-tos/api-keys)
# Note: These are for Arch Linux use ONLY. For your own distribution, please
# get your own set of keys.
_google_api_key=apikey
_google_default_client_id=noid
_google_default_client_secret=nosecret

# Taken from chromium-dev PKGBUILD
if [ ! -f "${BUILDDIR}/PKGBUILD" ]; then
  _builddir="/${pkgname}"
fi

_clang_path="${BUILDDIR}${_builddir}/src/chromium-${pkgver}/third_party/llvm-build/Release+Asserts/bin/"

prepare() {
  cd "$srcdir/chromium-$pkgver"

  # Allow building against system libraries in official builds
  sed -i 's/OFFICIAL_BUILD/GOOGLE_CHROME_BUILD/' \
    tools/generate_shim_headers/generate_shim_headers.py

  # https://crbug.com/893950
  sed -i -e 's/\<xmlMalloc\>/malloc/' -e 's/\<xmlFree\>/free/' \
    third_party/blink/renderer/core/xml/*.cc \
    third_party/blink/renderer/core/xml/parser/xml_document_parser.cc \
    third_party/libxml/chromium/*.cc
  
  # Fixes for building with libstdc++ instead of libc++
  patch -Np1 -i ../patches/chromium-90-ruy-include.patch
  patch -Np1 -i ../patches/chromium-94-CustomSpaces-include.patch
  patch -Np1 -i ../patches/chromium-94-compiler.patch
  
  # Custom fixes
  patch -Np1 -i ../chromium-94-sql-assert.patch

  mkdir -p third_party/node/linux/node-linux-x64/bin
  ln -sf /usr/bin/node third_party/node/linux/node-linux-x64/bin/
  ln -s /usr/bin/java third_party/jdk/current/bin/

  # Remove bundled libraries for which we will use the system copies; this
  # *should* do what the remove_bundled_libraries.py script does, with the
  # added benefit of not having to list all the remaining libraries
  local _lib
  for _lib in ${_unwanted_bundled_libs[@]}; do
    find "third_party/$_lib" -type f \
      \! -path "third_party/$_lib/chromium/*" \
      \! -path "third_party/$_lib/google/*" \
      \! -path "third_party/harfbuzz-ng/utils/hb_scoped.h" \
      \! -regex '.*\.\(gn\|gni\|isolate\)' \
      -delete
  done

  python2 build/linux/unbundle/replace_gn_files.py \
    --system-libraries "${!_system_libs[@]}"

  # Download prebuilt clang from Google, as system clang does not work here.
  tools/clang/scripts/update.py

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
      -i ui/gtk/gtk_util.cc
  sed -e 's|chromium|&-canary|' \
      -i chrome/common/chrome_paths_linux.cc
  sed -e 's|/etc/chromium|&-canary|' \
      -e 's|/usr/share/chromium|&-canary|' \
      -i chrome/common/chrome_paths.cc
  sed -e 's|/etc/chromium|&-canary|' \
      -e "s|'app_name': 'Chromium|&-canary|g" \
      -i components/policy/tools/template_writers/writer_configuration.py

  # If using bundled ffmpeg, create link to system opus headers. Compiling fails without this.
  if [[ -y ${_system_libs[ffmpeg]+set} ]]; then
    rm -fr third_party/opus/src/include
    ln -sf /usr/include/opus/ third_party/opus/src/include
  fi
}

build() {
  make -C chromium-launcher-$_launcher_ver CHROMIUM_SUFFIX="-canary"

  cd "$srcdir/chromium-$pkgver"

  if check_buildoption ccache y; then
    # Avoid falling back to preprocessor mode when sources contain time macros
    export CCACHE_SLOPPINESS=time_macros
  fi

  #export CC="${_clang_path}clang"
  #export CXX="${_clang_path}clang++"
  #export AR="${_clang_path}llvm-ar"
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
    'ffmpeg_branding="Chrome"'
    'proprietary_codecs=true'
    'rtc_use_pipewire=true'
    'link_pulseaudio=true'
    'use_gnome_keyring=false'
    'use_sysroot=false'
    'use_custom_libcxx=false'
    'enable_hangout_services_extension=true'
    'enable_widevine=true'
    'use_vaapi=true'
    'enable_nacl=false'
    "google_api_key=\"${_google_api_key}\""
    "google_default_client_id=\"${_google_default_client_id}\""
    "google_default_client_secret=\"${_google_default_client_secret}\""
    'build_with_tflite_lib=false'
    'is_cfi=false'
  )

  if [[ -n ${_system_libs[icu]+set} ]]; then
    _flags+=('icu_use_data_file=false')
  fi

  if check_option strip y; then
    _flags+=('symbol_level=0')
  fi

  # Taken from chromium-dev
  if [[ -y ${_system_libs[ffmpeg]+set} ]]; then
    msg2 "Build bundled ffmpeg, compilation fails with system ffmpeg"
    pushd third_party/ffmpeg &> /dev/null
    # Disable lto.
    # NOTE: This avoid messages like:
    # bfd plugin: LLVM gold plugin has failed to create LTO module: Unknown attribute kind (60) (Producer: 'LLVM9.0.0svn' Reader: 'LLVM 8.0.0')
    # when you have installed clang in the system.
    chromium/scripts/build_ffmpeg.py linux x64 --branding Chrome -- \
      --disable-lto

    chromium/scripts/copy_config.sh
    chromium/scripts/generate_gn.py
    popd &> /dev/null
  fi

  # Facilitate deterministic builds (taken from build/config/compiler/BUILD.gn)
  CFLAGS+='   -Wno-builtin-macro-redefined'
  CXXFLAGS+=' -Wno-builtin-macro-redefined'
  CPPFLAGS+=' -D__DATE__=  -D__TIME__=  -D__TIMESTAMP__='

  # Do not warn about unknown warning options
  CFLAGS+='   -Wno-unknown-warning-option'
  CXXFLAGS+=' -Wno-unknown-warning-option'

  gn gen out/Release --args="${_flags[*]}"
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
    out/Release/lib{EGL,GLESv2}.so \
    "$pkgdir/usr/lib/chromium-canary/"
  install -Dm644 -t "$pkgdir/usr/lib/chromium-canary/locales" out/Release/locales/*.pak
  install -Dm755 -t "$pkgdir/usr/lib/chromium-canary/swiftshader" out/Release/swiftshader/*.so

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
