%global package_speccommit 39d69af8869e33cfcd332d3f8b88cab941c9a27b
%global usver 3.10
%global xsver 2
%global xsrel %{xsver}%{?xscount}%{?xshash}
# Recent so-version, so we do not bump accidentally.
%global nettle_so_ver 8
%global hogweed_so_ver 6

%bcond_with fips

Name:           nettle
Version:        3.10
Release: %{?xsrel}.1%{?dist}
Summary:        A low-level cryptographic library

License:        LGPLv3+ or GPLv2+
URL:            http://www.lysator.liu.se/~nisse/nettle/
Source0: nettle-3.10-hobbled.tar.xz

BuildRequires:  make
%if 0%{?xenserver} < 9
BuildRequires:  devtoolset-11-gcc
%else
BuildRequires:  gcc
%endif
BuildRequires:  gmp-devel, m4
BuildRequires:	libtool, automake, autoconf, gettext-devel
# Required to build libhogweed.so
BuildRequires:	gmp-devel >= 6.1.0
# Force dependency on api __gmpn_cnd_swap (used since nettle-3.6, this API was not present in gmp-6.0.0)
Requires: gmp  >= 6.1.0
%if %{with fips}
BuildRequires:  fipscheck
%endif

%package devel
Summary:        Development headers for a low-level cryptographic library
Requires:       %{name} = %{version}-%{release}
Requires:       gmp-devel%{?_isa}

%description
Nettle is a cryptographic library that is designed to fit easily in more
or less any context: In crypto toolkits for object-oriented languages
(C++, Python, Pike, ...), in applications like LSH or GNUPG, or even in
kernel space.

%description devel
Nettle is a cryptographic library that is designed to fit easily in more
or less any context: In crypto toolkits for object-oriented languages
(C++, Python, Pike, ...), in applications like LSH or GNUPG, or even in
kernel space.  This package contains the files needed for developing
applications with nettle.


%prep
%autosetup -Tb 0 -p1

# Disable -ggdb3 which makes debugedit unhappy
sed s/ggdb3/g/ -i configure
sed 's/ecc-secp192r1.c//g' -i Makefile.in
sed 's/ecc-secp224r1.c//g' -i Makefile.in

%build
%if 0%{?xenserver} < 9
source /opt/rh/devtoolset-11/enable
%endif
autoreconf -ifv
export ASM_FLAGS="-Wa,--generate-missing-build-notes=yes"
%configure --enable-shared --enable-fat
%make_build

%if %{with fips}
%define fipshmac() \
	fipshmac -d $RPM_BUILD_ROOT%{_libdir} $RPM_BUILD_ROOT%{_libdir}/%1.* \
	file=`basename $RPM_BUILD_ROOT%{_libdir}/%1.*.hmac` && \
	mv $RPM_BUILD_ROOT%{_libdir}/$file $RPM_BUILD_ROOT%{_libdir}/.$file && \
	ln -s .$file $RPM_BUILD_ROOT%{_libdir}/.%1.hmac

%define __spec_install_post \
	%{?__debug_package:%{__debug_install_post}} \
	%{__arch_install_post} \
	%{__os_install_post} \
	%fipshmac libnettle.so.%{nettle_so_ver} \
	%fipshmac libhogweed.so.%{hogweed_so_ver} \
	%{?bootstrap_fips:%fipshmac libnettle.so.%{nettle_so_ver_old}} \
	%{?bootstrap_fips:%fipshmac libhogweed.so.%{hogweed_so_ver_old}} \
%{nil}
%endif


%install

%make_install
make install-shared DESTDIR=$RPM_BUILD_ROOT INSTALL="install -p"
mkdir -p $RPM_BUILD_ROOT%{_infodir}
install -p -m 644 nettle.info $RPM_BUILD_ROOT%{_infodir}/
rm -f $RPM_BUILD_ROOT%{_libdir}/*.a
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
rm -f $RPM_BUILD_ROOT%{_bindir}/nettle-lfib-stream
rm -f $RPM_BUILD_ROOT%{_bindir}/pkcs1-conv
rm -f $RPM_BUILD_ROOT%{_bindir}/sexp-conv
rm -f $RPM_BUILD_ROOT%{_bindir}/nettle-hash
rm -f $RPM_BUILD_ROOT%{_bindir}/nettle-pbkdf2

chmod 0755 $RPM_BUILD_ROOT%{_libdir}/libnettle.so.%{nettle_so_ver}.*
chmod 0755 $RPM_BUILD_ROOT%{_libdir}/libhogweed.so.%{hogweed_so_ver}.*

%check
make check

%files
%doc AUTHORS NEWS README
%license COPYINGv2 COPYING.LESSERv3
%{_infodir}/nettle.info.*
%{_libdir}/libnettle.so.%{nettle_so_ver}
%{_libdir}/libnettle.so.%{nettle_so_ver}.*
%{_libdir}/libhogweed.so.%{hogweed_so_ver}
%{_libdir}/libhogweed.so.%{hogweed_so_ver}.*
%if %{with fips}
%{_libdir}/.libhogweed.so.*.hmac
%{_libdir}/.libnettle.so.*.hmac
%endif

%files devel
%doc descore.README nettle.html nettle.pdf
%{_includedir}/nettle
%{_libdir}/libnettle.so
%{_libdir}/libhogweed.so
%{_libdir}/pkgconfig/hogweed.pc
%{_libdir}/pkgconfig/nettle.pc

%ldconfig_scriptlets


%changelog
* Mon Jun 22 2026 Philippe Coval <philippe.coval@vates.tech> - 3.10-2.1
- Add Requires on gmp version with __gmpn_cnd_swap

* Tue Nov 11 2025 Lin Liu <lin.liu01@citrix.com> - 3.10-2
- CP-310102: Build compatible with XS8 and specify gmp-devel version

* Thu Jan 16 2025 Lin Liu <lin.liu@citrix.com> - 3.10-1
- CP-53179: Update to 3.10

* Thu Sep 26 2024 Stephen Cheng <stephen.cheng@cloud.com> - 3.8-2
- CP-51608: Removed fips dependency

* Tue Jun 27 2023 Lin Liu <lin.liu@citrix.com> - 3.8-1
- First imported release

