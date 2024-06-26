# Maintainer: Evangelos Foutras <evangelos@foutrelis.com>
# Contributor: Pierre Schmitz <pierre@archlinux.de>
# Contributor: Jan "heftig" Steffens <jan.steffens@gmail.com>
# Contributor: Daniel J Griffiths <ghost1227@archlinux.us>

pkgname=chromium-canary
pkgver=126.0.6443.0
pkgrel=1
_launcher_ver=8
_gcc_patchset=1
_use_libcxx=1
pkgdesc="A web browser built for speed, simplicity, and security"
arch=('x86_64')
url="https://www.chromium.org/Home"
license=('BSD')
depends=('gtk3' 'nss' 'alsa-lib' 'xdg-utils' 'libxss' 'libcups' 'libgcrypt'
         'ttf-liberation' 'systemd' 'dbus' 'libpulse' 'pciutils' 'libva'
         'desktop-file-utils' 'hicolor-icon-theme' 'libffi')
makedepends=('python' 'gperf' 'ninja' 'nodejs' 'git' 'rust' 'qt5-base'
             'pipewire' 'clang' 'lld' 'gn' 'java-runtime-headless')
optdepends=('pipewire: WebRTC desktop sharing under Wayland'
            'kdialog: needed for file dialogs in KDE'
            'qt5-base: enable Qt5 with --enable-features=AllowQt'
            'gtk4: for --gtk-version=4 (GTK4 IME might work better on Wayland)'
            'org.freedesktop.secrets: password storage backend on GNOME / Xfce'
            'kwallet: for storing passwords in KWallet on KDE desktops')
if [[ ${USE_CCACHE} == yes ]]; then
  BUILDENV=(ccache)
fi
options=('!lto')
source=(https://commondatastorage.googleapis.com/chromium-browser-official/chromium-$pkgver.tar.xz
        chromium-launcher-$_launcher_ver.tar.gz::https://github.com/foutrelis/chromium-launcher/archive/v$_launcher_ver.tar.gz
        # Patchset
        #https://gitlab.com/Matt.Jolly/chromium-patches/-/archive/${pkgver%%.*}/chromium-patches-${pkgver%%.*}.tar.bz2
        https://gitlab.com/Matt.Jolly/chromium-patches/-/archive/124/chromium-patches-124.tar.bz2
        # Custom patches (might be from upstream)
        compiler-rt-adjust-paths.patch
        drop-flag-unsupported-by-clang17.patch
        chromium-126-xslt.patch
        )

sha256sums=("$(curl -sL https://commondatastorage.googleapis.com/chromium-browser-official/chromium-${pkgver}.tar.xz.hashes | grep sha256 | cut -d ' ' -f3)"
            '213e50f48b67feb4441078d50b0fd431df34323be15be97c55302d3fdac4483a'
            # Hash for patchset
            'c2bc4e65ed2a4e23528dd10d5c15bf99f880b7bbb789cc720d451b78098a7e12'
            # Hash(es) for custom patches
            'b3de01b7df227478687d7517f61a777450dca765756002c80c4915f271e2d961'
            'e8eca0c437e390ae1d760aa0befcb858ca8d511da08362876a260be1f219e9e0'
            '8cc18d52758857bdd242c0eb301aaef4f8aa0ec6e9685958ca56fea6f26a70e9'
            )

# Possible replacements are listed in build/linux/unbundle/replace_gn_files.py
# Keys are the names in the above script; values are the dependencies in Arch
declare -gA _system_libs=(
  [brotli]=brotli
  [dav1d]=dav1d
  #[ffmpeg]=ffmpeg
  [flac]=flac
  [fontconfig]=fontconfig
  [freetype]=freetype2
  [harfbuzz-ng]=harfbuzz
  [icu]=icu
  #[libaom]=aom
  #[libavif]=libavif  # needs https://github.com/AOMediaCodec/libavif/commit/5410b23f76
  [libdrm]=
  [libjpeg]=libjpeg
  [libpng]=libpng
  #[libvpx]=libvpx
  #[libwebp]=libwebp  # //third_party/libavif:libavif_enc needs //third_party/libwebp:libwebp_sharpyuv
  [libxml]=libxml2
  [libxslt]=libxslt
  [opus]=opus
  [zlib]=minizip
)

# Unbundle only without libc++, as libc++ is not fully ABI compatible with libstdc++
if (( !_use_libcxx )); then
  _system_libs+=(
    [jsoncpp]=jsoncpp
    #[re2]=re2  # //third_party/googletest:gtest_config needs //third_party/re2:re2_config
    [snappy]=snappy
    [woff2]=woff2
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
  #if [[ ${GOOGLE_CLANG} != yes ]]; then
  #  patch -Np0 -i ../chromium-113-clang.patch
  #fi

  # Apply patches if libc++ is not used.
  if (( !_use_libcxx )); then
    patch -Np1 -i ../chromium-patches-*/chromium-117-material-color-include.patch
  fi

  # Apply patches if GCC is used.
  #patch -Np2 -i ../chromium-109-gcc-math.patch

  # Custom or upstream patches.
  patch -Np1 -i ../compiler-rt-adjust-paths.patch
  patch -Np0 -i ../drop-flag-unsupported-by-clang17.patch
  patch -Np2 -i ../chromium-126-xslt.patch

  # Link to system tools required by the build
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
    ./tools/clang/scripts/update.py
    ./tools/rust/update_rust.py
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
    export NM="${_clang_path}llvm-nm"
  else
    export CC=clang
    export CXX=clang++
    export AR=ar
    export NM=nm
  fi

  local _flags=(
    'custom_toolchain="//build/toolchain/linux/unbundle:default"'
    'host_toolchain="//build/toolchain/linux/unbundle:default"'
    'is_official_build=true' # implies is_cfi=true on x86_64
    'symbol_level=0' # sufficient for backtraces on x86(_64)
    'treat_warnings_as_errors=false'
    'disable_fieldtrial_testing_config=true'
    'blink_enable_generated_code_formatting=false'
    'ffmpeg_branding="Chrome"'
    'proprietary_codecs=true'
    'rtc_use_pipewire=true'
    'link_pulseaudio=true'
    'use_sysroot=false'
    'enable_hangout_services_extension=true'
    'enable_widevine=true'
    'enable_nacl=false'
    "google_api_key=\"${_google_api_key}\""
    'use_system_libffi=true'
    'use_vaapi=true'
    'use_ozone=true'
    'ozone_auto_platforms=false'
    'ozone_platform_headless=true'
    'ozone_platform_wayland=true'
    'ozone_platform_x11=true'
    'ozone_platform="x11"'
  )

  # Use these settings if system Clang is used.
  if [[ ${GOOGLE_CLANG} != yes ]]; then
    local _clang_version=$(
      clang --version | grep -m1 version | sed 's/.* \([0-9]\+\).*/\1/')

    _flags+=(
      'chrome_pgo_phase=0'
      'clang_base_path="/usr"'
      'clang_use_chrome_plugins=false'
      "clang_version=\"$_clang_version\"")
    
    # Allow the use of nightly features with stable Rust compiler
    # https://github.com/ungoogled-software/ungoogled-chromium/pull/2696#issuecomment-1918173198
    export RUSTC_BOOTSTRAP=1

    _flags+=(
      'rust_sysroot_absolute="/usr"'
      "rustc_version=\"$(rustc --version)\""
    )
  fi

  if [[ -n ${_system_libs[icu]+set} ]]; then
    _flags+=('icu_use_data_file=false')
  fi

  if [[ _use_libcxx ]]; then
    _flags+=('use_custom_libcxx=true')
  else
    _flags+=('use_custom_libcxx=false')
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
    out/Release/libqt5_shim.so \
    out/Release/{libvk_swiftshader.so,libvulkan.so.1,vk_swiftshader_icd.json} \
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
