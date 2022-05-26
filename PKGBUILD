# Maintainer: Evangelos Foutras <evangelos@foutrelis.com>
# Contributor: Pierre Schmitz <pierre@archlinux.de>
# Contributor: Jan "heftig" Steffens <jan.steffens@gmail.com>
# Contributor: Daniel J Griffiths <ghost1227@archlinux.us>

pkgname=chromium-canary
pkgver=104.0.5084.0
pkgrel=1
_launcher_ver=8
_gcc_patchset=1
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
#BUILDENV=(ccache)
options=('!lto')
source=(https://commondatastorage.googleapis.com/chromium-browser-official/chromium-$pkgver.tar.xz
        chromium-launcher-$_launcher_ver.tar.gz::https://github.com/foutrelis/chromium-launcher/archive/v$_launcher_ver.tar.gz
        # Patchset
        #https://github.com/stha09/chromium-patches/releases/download/chromium-${pkgver%%.*}-patchset-$_gcc_patchset/chromium-${pkgver%%.*}-patchset-$_gcc_patchset.tar.xz
        #https://github.com/stha09/chromium-patches/releases/download/chromium-102-patchset-$_gcc_patchset/chromium-102-patchset-$_gcc_patchset.tar.xz
        # Custom patches (might be from upstream)
        sql-make-VirtualCursor-standard-layout-type.patch
        chromium-102-no-opaque-pointers.patch
        )

sha256sums=("$(curl -sL https://commondatastorage.googleapis.com/chromium-browser-official/chromium-${pkgver}.tar.xz.hashes | grep sha256 | cut -d ' ' -f3)"
            '213e50f48b67feb4441078d50b0fd431df34323be15be97c55302d3fdac4483a'
            # Hash for patchset
            #'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
            # Hash(es) for custom patches
            'b94b2e88f63cfb7087486508b8139599c89f96d7a4181c61fec4b4e250ca327a'
            'a108edd984e42884089a5de063f9c069a936d29dd066b68c90b5dac6529a8d05'
            )

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
  #[zlib]=minizip
)

# Unbundle only without libc++, as libc++ is not fully ABI compatible with libstdc++
if [[ ${FORCE_LIBCXX} != yes ]]; then
  _system_libs+=(
    [re2]=re2
    [snappy]=snappy
  )
fi

_unwanted_bundled_libs=(
  $(printf "%s\n" ${!_system_libs[@]} | sed 's/^libjpeg$/&_turbo/')
)
depends+=(${_system_libs[@]})

# Google API keys (see https://www.chromium.org/developers/how-tos/api-keys)
# Note: These are for Arch Linux use ONLY. For your own distribution, please
# get your own set of keys.
_google_api_key=apikey

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
    third_party/libxml/chromium/*.cc \
    third_party/maldoca/src/maldoca/ole/oss_utils.h

  # Apply patches if Google Clang is not used.
  if [[ ${GOOGLE_CLANG} != yes ]]; then
    patch -Np1 -i ../sql-make-VirtualCursor-standard-layout-type.patch
  fi

  # Apply patches if libc++ is not used.
  #if [[ ${FORCE_LIBCXX} != yes ]]; then
  #  patch -Np0 -i ../chromium-104-IWYU-autofill.patch
  #fi

  # Custom or upstream patches.
  patch -Np0 -i ../chromium-102-no-opaque-pointers.patch

  # Alternative to removing the orchestrator.
  touch third_party/blink/tools/merge_web_test_results.pydeps
  mkdir -p third_party/blink/tools/blinkpy/web_tests
  touch third_party/blink/tools/blinkpy/web_tests/merge_results.pydeps

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

  python build/linux/unbundle/replace_gn_files.py \
    --system-libraries "${!_system_libs[@]}"

  # Download Google's prebuilt Clang if needed.
  if [[ ${GOOGLE_CLANG} == yes ]]; then
    tools/clang/scripts/update.py
  fi

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
  if [[ -z ${_system_libs[ffmpeg]+set} ]]; then
    rm -fr third_party/opus/src/include
    ln -sf /usr/include/opus/ third_party/opus/src/include
  fi
}

build() {
  make -C chromium-launcher-$_launcher_ver CHROMIUM_SUFFIX="-canary"

  # Doing this should lower the amount of misses for ccache.
  if check_buildoption ccache y; then
    export CCACHE_BASEDIR="$(pwd)"
  fi

  cd "$srcdir/chromium-$pkgver"

  if check_buildoption ccache y; then
    # Avoid falling back to preprocessor mode when sources contain time macros
    export CCACHE_SLOPPINESS=time_macros
  fi

  # Switch between Google's Clang and system Clang.
  if [[ ${GOOGLE_CLANG} == yes ]]; then
    export CC="${_clang_path}clang"
    export CXX="${_clang_path}clang++"
    export AR="${_clang_path}llvm-ar"
  else
    export CC=clang
    export CXX=clang++
    export AR=ar
  fi
  export NM=nm

  local _flags=(
    'custom_toolchain="//build/toolchain/linux/unbundle:default"'
    'host_toolchain="//build/toolchain/linux/unbundle:default"'
    'clang_use_chrome_plugins=false'
    'is_official_build=true' # implies is_cfi=true on x86_64
    'symbol_level=0' # sufficient for backtraces on x86(_64)
    'treat_warnings_as_errors=false'
    'disable_fieldtrial_testing_config=true'
    'blink_enable_generated_code_formatting=false'
    'ffmpeg_branding="Chrome"'
    'proprietary_codecs=true'
    'rtc_use_pipewire=true'
    'link_pulseaudio=true'
    'use_gnome_keyring=false'
    'use_sysroot=false'
    'enable_hangout_services_extension=true'
    'enable_widevine=true'
    'enable_nacl=false'
    "google_api_key=\"${_google_api_key}\""
    'use_vaapi=true'
    'use_ozone=true'
    'ozone_auto_platforms=false'
    'ozone_platform_headless=true'
    'ozone_platform_x11=true'
    'ozone_platform="x11"'
  )

  # PGO profiles cannot be read with system Clang.
  if [[ ${GOOGLE_CLANG} != yes ]]; then
    _flags+=('chrome_pgo_phase=0')
  fi

  if [[ -n ${_system_libs[icu]+set} ]]; then
    _flags+=('icu_use_data_file=false')
  fi

  if [[ ${FORCE_LIBCXX} == yes ]]; then
    _flags+=('use_custom_libcxx=true')
  else
    _flags+=('use_custom_libcxx=false')
  fi

  # Taken from chromium-dev
  if [[ -z ${_system_libs[ffmpeg]+set} ]]; then
    msg2 "Build bundled ffmpeg, compilation fails with system ffmpeg"
    pushd third_party/ffmpeg &> /dev/null
    chromium/scripts/build_ffmpeg.py linux x64 --branding Chrome -- \
      --disable-asm

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

  # Let Chromium set its own symbol level
  CFLAGS=${CFLAGS/-g }
  CXXFLAGS=${CXXFLAGS/-g }

  # Get rid of the "-fexceptions" flag.
  CFLAGS=${CFLAGS/-fexceptions}
  CFLAGS=${CFLAGS/-fcf-protection}
  CXXFLAGS=${CXXFLAGS/-fexceptions}
  CXXFLAGS=${CXXFLAGS/-fcf-protection}

  # This appears to cause random segfaults when combined with ThinLTO
  # https://bugs.archlinux.org/task/73518
  CFLAGS=${CFLAGS/-fstack-clash-protection}
  CXXFLAGS=${CXXFLAGS/-fstack-clash-protection}

  # https://crbug.com/957519#c122
  CXXFLAGS=${CXXFLAGS/-Wp,-D_GLIBCXX_ASSERTIONS}

  # Specific to libstdc++
  CXXFLAGS+=' -fbracket-depth=512'

  gn gen out/Release --args="${_flags[*]}"
  ninja -C out/Release chrome chrome_sandbox chromedriver.unstripped
}

package() {
  cd chromium-launcher-$_launcher_ver
  make PREFIX=/usr DESTDIR="$pkgdir" CHROMIUM_SUFFIX="-canary" install
  install -Dm644 LICENSE \
    "$pkgdir/usr/share/licenses/chromium-canary/LICENSE.launcher"

  cd "$srcdir/chromium-$pkgver"

  # Install binaries
  install -D out/Release/chromium-canary "$pkgdir/usr/lib/chromium-canary/chromium-canary"
  install -D out/Release/chromedriver.unstripped "$pkgdir/usr/bin/chromedriver-canary"
  install -Dm4755 out/Release/chrome_sandbox "$pkgdir/usr/lib/chromium-canary/chrome-sandbox"

  # Install .desktop and manpages.
  install -Dm644 chrome/installer/linux/common/desktop.template \
    "$pkgdir/usr/share/applications/chromium-canary.desktop"
  install -Dm644 chrome/app/resources/manpage.1.in \
    "$pkgdir/usr/share/man/man1/chromium-canary.1"
  sed -i \
    -e "s/@@MENUNAME@@/Chromium Canary/g" \
    -e "s/@@PACKAGE@@/chromium-canary/g" \
    -e "s/@@USR_BIN_SYMLINK_NAME@@/chromium-canary/g" \
    "$pkgdir/usr/share/applications/chromium-canary.desktop" \
    "$pkgdir/usr/share/man/man1/chromium-canary.1"

  install -Dm644 chrome/installer/linux/common/chromium-browser/chromium-browser.appdata.xml \
    "$pkgdir/usr/share/metainfo/chromium-canary.appdata.xml"
  sed -ni \
    -e 's/chromium-browser\.desktop/chromium-canary.desktop/' \
    -e '/<update_contact>/d' \
    -e '/<p>/N;/<p>\n.*\(We invite\|Chromium supports Vorbis\)/,/<\/p>/d' \
    -e '/^<?xml/,$p' \
    "$pkgdir/usr/share/metainfo/chromium-canary.appdata.xml"

  # Install resources and locales.
  cp \
    out/Release/{chrome_{100,200}_percent,resources}.pak \
    out/Release/{v8_context_snapshot.bin,chrome_crashpad_handler} \
    out/Release/lib{EGL,GLESv2}.so \
    out/Release/{libvk_swiftshader.so,vk_swiftshader_icd.json} \
    "$pkgdir/usr/lib/chromium-canary/"

  if [[ -z ${_system_libs[icu]+set} ]]; then
    cp out/Release/icudtl.dat "$pkgdir/usr/lib/chromium-canary/"
  fi

  install -Dm644 -t "$pkgdir/usr/lib/chromium-canary/locales" out/Release/locales/*.pak
  #install -Dm755 -t "$pkgdir/usr/lib/chromium-canary/swiftshader" out/Release/swiftshader/*.so

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
