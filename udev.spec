%define url ftp://ftp.kernel.org/pub/linux/utils/kernel/hotplug
%define tarname %{name}-%{version}
%define kernel_dir /usr/src/linux
%define use_dietlibc 0
%define bootstrap 0

%define main_major 0
%define gudev_api 1.0
%define gudev_major 0

%define libname %mklibname %{name} %{main_major}
%define gudev_libname %mklibname gudev %{gudev_api} %{main_major}
%define gudev_libname_devel %mklibname gudev %{gudev_api} -d

%define lib_udev_dir /lib/%{name}
%define system_rules_dir %{lib_udev_dir}/rules.d
%define user_rules_dir %{_sysconfdir}/%{name}/rules.d

%{?_without_dietlibc:	%{expand: %%global use_dietlibc 0}}
%{?_with_dietlibc:		%{expand: %%global use_dietlibc 1}}

%{?_with_bootstrap:		%{expand: %%global bootstrap 1}}
%{?_without_bootstrap:	%{expand: %%global bootstrap 0}}

%define git_url git://git.kernel.org/pub/scm/linux/hotplug/udev.git

Name: 		udev
Version: 	150
Release: 	%manbo_mkrel 1
License: 	GPLv2
Summary: 	A userspace implementation of devfs
Group:		System/Configuration/Hardware
URL:		%{url}
Source0: 	%{url}/%{tarname}.tar.bz2
Source1: 	%{url}/%{tarname}.tar.bz2.sign
Source2:	50-udev-mandriva.rules
Source3:	69-printeracl.rules
Source5:	udev.sysconfig

# from Fedora (keep unmodified)
Source6:        udev-post.init
Source7:	start_udev

Source8:	default.nodes
Source9:	create_static_dev_nodes
Source34:	udev_import_usermap
# from hotplug-2004_09_23
Source40:	hotplug-usb.distmap
Source41:	hotplug-usb.handmap
# (blino) net rules and helpers
Source60:	76-net.rules
Source62:	udev_net_create_ifcfg
Source63:	udev_net_action
Source64:	udev_net.sysconfig
# (fc) 140-1mdv put back pam console apply for now
Source65:	95-pam-console.rules

# from upstream git

# from Mandriva
# disable coldplug for storage and device pci 
Patch20:	udev-146-coldplug.patch
# patches from Mandriva on Fedora's start_udev
Patch70:	udev-125-devices_d.patch
Patch71:	udev-142-MAKEDEV.patch
Patch73:	udev-137-speedboot.patch
# (fc) 146-3mdv fix invalid udev trigger call
Patch75:	udev-150-udevpost-trigger.patch

#Conflicts:  devfsd
Conflicts:	sound-scripts < 0.13-1mdk
Conflicts:	hotplug < 2004_09_23-22mdk
Conflicts:	pam < pam-0.99.3.0-1mdk
Conflicts:	initscripts < 8.51-7mdv2007.1
Obsoletes:	udev-extras <= 20090226
Provides:	udev-extras = 20090226-1mdv
Requires:	coreutils
Requires:	setup >= 2.7.16
Requires:	util-linux-ng >= 2.15
%if %use_dietlibc
BuildRequires:	dietlibc
%endif
BuildRequires:	glibc-static-devel
BuildRequires:  libblkid-devel
%if !%{bootstrap}
BuildRequires:  libacl-devel
BuildRequires:  glib2-devel
BuildRequires:  libusb-devel
BuildRequires:  gperf
BuildRequires:  gobject-introspection-devel >= 0.6.2
BuildRequires:  libtool
BuildRequires:	gtk-doc
BuildRequires:	ldetect-lst >= 0.1.283
Requires:	ldetect-lst >= 0.1.283
%endif
BuildRoot: 	%{_tmppath}/%{name}-%{version}-build
Obsoletes:	speedtouch eagle-usb
Obsoletes: %{name}-tools < 125
Provides: %{name}-tools = %{version}-%{release}

%description
Udev is an implementation of devfs/devfsd in userspace using sysfs and
/sbin/hotplug. It requires a 2.6 kernel to run properly.

Like devfs, udev dynamically creates and removes device nodes from /dev/.
It responds to /sbin/hotplug device events.

%package doc
Summary: Udev documentation
Group: Books/Computer books
%description doc
This package contains documentation of udev.

%package -n %{libname}
Group: System/Libraries
Summary: Library for %{name}
License: LGPLv2+
%description -n %{libname}
Library for %{name}.

%package -n %{libname}-devel
Group: Development/C
Summary: Devel library for %{name}
License: LGPLv2+
Provides: %{name}-devel = %{version}-%{release}
Provides: lib%{name}-devel = %{version}-%{release}
Requires: %{libname} = %{version}
%description -n %{libname}-devel
Devel library for %{udev}.

%package -n %{gudev_libname}
Summary: Libraries for adding libudev support to applications that use glib
Group: System/Libraries
License: LGPLv2+
Requires: %{libname} >= 142

%description -n %{gudev_libname}
This package contains the libraries that make it easier to use libudev
functionality from applications that use glib.

%package -n %{gudev_libname_devel}
Summary: Header files for adding libudev support to applications that use glib
Group: Development/C
License: LGPLv2+
Requires: %{libname}-devel >= 142
Requires: %{gudev_libname} = %{version}-%{release}
Provides: libgudev-devel = %{version}-%{release}

%description -n %{gudev_libname_devel}
This package contains the header and pkg-config files for developing
glib-based applications using libudev functionality.

%prep
%setup -q
%patch20 -p1 -b .coldplug
cp -a %{SOURCE7} .
cp -a %{SOURCE6} .
%patch70 -p1 -b .devices_d
%patch71 -p1 -b .MAKEDEV
%patch73 -p1 -b .speedboot
%patch75 -p1 -b .udevtrigger

%build
%serverbuild
%configure2_5x \
  --prefix=%{_prefix} \
  --sysconfdir=%{_sysconfdir} \
  --sbindir="/sbin" \
  --libexecdir="%{lib_udev_dir}" \
  --with-rootlibdir=/%{_lib} \
%if %{bootstrap}
  --disable-extras --disable-introspection 
%else
  --enable-extras --enable-introspection
%endif

%make

%install
rm -rf %{buildroot}
%makeinstall_std

%if %use_dietlibc
install -d %{buildroot}%{_prefix}/lib/dietlibc/lib-%{_arch}
%endif

install -m 755 start_udev %{buildroot}/sbin/
install -m 755 %SOURCE9 %{buildroot}/sbin/

install -m 644 %SOURCE2 %{buildroot}%{system_rules_dir}/
install -m 644 %SOURCE3 %{buildroot}%{system_rules_dir}/
# use RH rules for pam_console
install -m 644 %SOURCE65 %{buildroot}%{system_rules_dir}/95-pam-console.rules
# use upstream rules for sound devices, device mapper, raid devices
for f in \
  40-isdn \
  64-device-mapper \
  ; do
    install -m 644 rules/packages/$f.rules %{buildroot}%{system_rules_dir}/
done

install -d %{buildroot}%{_sysconfdir}/sysconfig
install -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/sysconfig/udev

# net rules
install -m 0644 %SOURCE60 %{buildroot}%{system_rules_dir}/
install -m 0755 %SOURCE62 %{buildroot}%{lib_udev_dir}/net_create_ifcfg
install -m 0755 %SOURCE63 %{buildroot}%{lib_udev_dir}/net_action
install -m 0644 %SOURCE64 %{buildroot}/etc/sysconfig/udev_net

mkdir -p %{buildroot}%{_sysconfdir}/%{name}/devices.d/
install -m 0755 %SOURCE8 %{buildroot}%{_sysconfdir}/%{name}/devices.d/

mkdir -p %{buildroot}%{_sbindir}
install -m 0755 %SOURCE34 %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/agents.d/usb

touch $RPM_BUILD_ROOT%{_sysconfdir}/scsi_id.config

%{buildroot}%{_sbindir}/udev_import_usermap --no-driver-agent usb %{SOURCE40} %{SOURCE41} > %{buildroot}%{system_rules_dir}/70-hotplug_map.rules

mkdir -p %{buildroot}%{_initrddir}
install -m 0755 udev-post.init %{buildroot}%{_initrddir}/udev-post

# (blino) usb_id are used by drakx
ln -s ..%{lib_udev_dir}/usb_id %{buildroot}/sbin/

mkdir -p %{buildroot}/lib/firmware

rm -rf $RPM_BUILD_ROOT%{_docdir}/udev
rm -f $RPM_BUILD_ROOT/%{_libdir}/*.la

%clean
rm -rf %{buildroot}

%post
%_post_service udev-post

%preun
%_preun_service udev-post

%pre
if [ -d /lib/hotplug/firmware ]; then
	echo "Moving /lib/hotplug/firmware to /lib/firmware"
	mkdir -p /lib/firmware
	mv /lib/hotplug/firmware/* /lib/firmware/ 2>/dev/null
	rmdir -p --ignore-fail-on-non-empty /lib/hotplug/firmware
	:
fi

%triggerpostun -- udev < 064-4mdk
for i in /etc/udev/rules.d/{dvd,mouse}.rules; do
    [[ -e $i ]] && mv ${i}{,.old};
done
:

%triggerpostun -- udev < 068-17mdk
rm -f /etc/rc.d/*/{K,S}*udev

%triggerpostun -- udev < 109-2mdv2008.0
perl -n -e '/^\s*device=(.*)/ and print "L mouse $1\n"' /etc/sysconfig/mouse > /etc/udev/devices.d/mouse.nodes

%triggerpostun -- udev < 126-1mdv2008.0
# make Mandriva rules compatible with upstream write_cd_rules helper
sed -i -e 's/ENV{MDV_CONFIGURED}="yes"/ENV{GENERATED}="1"/' /etc/udev/rules.d/61-block_config.rules
# set $1 so that udev-post is handled like for a new install
set 1
%_post_service udev-post

%files
%defattr(0644,root,root,0755)
%attr(0755,root,root) /sbin/udevadm
%attr(0755,root,root) /sbin/udevd
%attr(0755,root,root) /sbin/create_static_dev_nodes
%attr(0755,root,root) /sbin/start_udev
%attr(0755,root,root) %{_sbindir}/udev_import_usermap
%attr(0755,root,root) %{_initrddir}/udev-post
%dir %{_sysconfdir}/%{name}/agents.d
%dir %{_sysconfdir}/%{name}/agents.d/usb
%config(noreplace) %{_sysconfdir}/sysconfig/udev
%config(noreplace) %{_sysconfdir}/sysconfig/udev_net
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%ghost %config(noreplace,missingok) %attr(0644,root,root) %{_sysconfdir}/scsi_id.config
%dir %{system_rules_dir}
%{system_rules_dir}/*
%dir %{_sysconfdir}/%{name}
%dir %{user_rules_dir}
%dir %{_sysconfdir}/%{name}/devices.d
%config(noreplace) %{_sysconfdir}/%{name}/devices.d/*.nodes
%{_mandir}/man7/*
%{_mandir}/man8/*
%dir /lib/firmware
%dir %{lib_udev_dir}
%attr(0755,root,root) %{lib_udev_dir}/ata_id
%attr(0755,root,root) %{lib_udev_dir}/cdrom_id
%attr(0755,root,root) %{lib_udev_dir}/edd_id
%attr(0755,root,root) %{lib_udev_dir}/input_id
%attr(0755,root,root) %{lib_udev_dir}/path_id
%attr(0755,root,root) %{lib_udev_dir}/scsi_id
%attr(0755,root,root) %{lib_udev_dir}/usb_id
%attr(0755,root,root) %{lib_udev_dir}/collect
%attr(0755,root,root) %{lib_udev_dir}/create_floppy_devices
%attr(0755,root,root) %{lib_udev_dir}/firmware
%attr(0755,root,root) %{lib_udev_dir}/fstab_import
%attr(0755,root,root) %{lib_udev_dir}/rule_generator.functions
%attr(0755,root,root) %{lib_udev_dir}/write_cd_rules
%attr(0755,root,root) %{lib_udev_dir}/write_net_rules
%attr(0755,root,root) %{lib_udev_dir}/net_create_ifcfg
%attr(0755,root,root) %{lib_udev_dir}/net_action
%attr(0755,root,root) %{lib_udev_dir}/v4l_id
%attr(0755,root,root) /sbin/usb_id
%if !%{bootstrap}
%attr(0755,root,root) %{lib_udev_dir}/hid2hci
%attr(0755,root,root) %{lib_udev_dir}/modem-modeswitch
%attr(0755,root,root) %{lib_udev_dir}/pci-db
%attr(0755,root,root) %{lib_udev_dir}/usb-db
%attr(0755,root,root) %{lib_udev_dir}/keymap
%attr(0755,root,root) %{lib_udev_dir}/udev-acl
%attr(0755,root,root) %{lib_udev_dir}/findkeyboards
%attr(0755,root,root) %{lib_udev_dir}/keyboard-force-release.sh
%dir %attr(0755,root,root) %{lib_udev_dir}/keymaps
%attr(0755,root,root) %{lib_udev_dir}/keymaps/*
%attr(0644,root,root) %{_prefix}/lib/ConsoleKit/run-seat.d/udev-acl.ck
%endif

%files doc
%defattr(0644,root,root,0755)
%doc COPYING README TODO ChangeLog NEWS extras/keymap/README.keymap.txt
%doc docs/writing_udev_rules/*

%files -n %{libname}
%defattr(0644,root,root,0755)
/%{_lib}/lib%{name}.so.%{main_major}*

%files -n %{libname}-devel
%defattr(0644,root,root,0755)
%doc %{_datadir}/gtk-doc/html/libudev
%{_libdir}/lib%{name}.*
%if %use_dietlibc
%{_prefix}/lib/dietlibc/lib-%{_arch}/lib%{name}.a
%endif
%{_libdir}/pkgconfig/lib%{name}.pc
%{_datadir}/pkgconfig/udev.pc
%{_includedir}/lib%{name}.h

%if !%{bootstrap}
%files -n %{gudev_libname}
%defattr(0644,root,root,0755)
%{_libdir}/libgudev-%{gudev_api}.so.%{gudev_major}*
%{_libdir}/girepository-1.0/GUdev-%{gudev_api}.typelib

%files -n %{gudev_libname_devel}
%defattr(0644,root,root,0755)
%doc %{_datadir}/gtk-doc/html/gudev
%{_libdir}/libgudev-%{gudev_api}.so
%{_includedir}/gudev-%{gudev_api}
%{_datadir}/gir-1.0/GUdev-%{gudev_api}.gir
%{_libdir}/pkgconfig/gudev-%{gudev_api}.pc
%endif
