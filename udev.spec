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

%define _with_systemd 1

Name: 		udev
Version: 	165
Release: 	%manbo_mkrel 4
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

Source34:	udev_import_usermap
# from hotplug-2004_09_23
Source40:	hotplug-usb.distmap
Source41:	hotplug-usb.handmap
# (blino) net rules and helpers
Source60:	76-net.rules
Source62:	udev_net_create_ifcfg
Source63:	udev_net_action
Source64:	udev_net.sysconfig
# (hk) udev rules for zte 3g modems with drakx-net
Source66:	61-mobile-zte-drakx-net.rules

# from upstream git
Patch0:		udev-165-dev-sg-ACL.patch
Patch1:		0001-v4l_id-kill-the-v4l1-ioctl.patch
Patch2:		0002-v4l_id-remove-left-over-variable.patch

# from Mandriva
# disable coldplug for storage and device pci 
Patch20:	udev-152-coldplug.patch
# patches from Mandriva on Fedora's start_udev
Patch73:	udev-137-speedboot.patch
# (bor) TODO to be removed when last STARTUP rule is fixed
Patch78:	udev-161-env_STARTUP.patch
# (bor) use action "add" instead of "change" when retrying failed events
Patch79:	udev-161-use-add-for-retry.patch
# (bor) udev-post should start after D-Bus
Patch80:	udev-162-udev-post_needs_dbus.patch
# (eugeni) allow to boot from live cd in virtualbox
Patch81:	udev-162-VirtualBox-boot-fix.patch

#Conflicts:  devfsd
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
%if %{_with_systemd}
BuildRequires:	systemd-units
%endif
%if !%{bootstrap}
BuildRequires:  libacl-devel
BuildRequires:  glib2-devel
BuildRequires:  libusb-devel
BuildRequires:  gperf
BuildRequires:  gobject-introspection-devel >= 0.6.2
BuildRequires:  libtool
BuildRequires:	gtk-doc
BuildRequires:	usbutils
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
Provides: libgudev = %{version}-%{release}

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
%patch73 -p1 -b .speedboot
%patch78 -p1 -b .STARTUP
%patch79 -p1 -b .action_add
%patch80 -p1 -b .messagebus
%patch81 -p1 -b .virtualbox_boot
%patch0  -p1 -b .dev_sg_ACL
%patch1  -p1 -b .v4l
%patch2  -p1 -b .v4l_vlcap

%build
%serverbuild
%configure2_5x \
  --prefix=%{_prefix} \
  --sysconfdir=%{_sysconfdir} \
  --sbindir="/sbin" \
  --libexecdir="%{lib_udev_dir}" \
%if !%{_with_systemd}
  --without-systemdsystemunitdir \
%endif
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

install -m 644 %SOURCE2 %{buildroot}%{system_rules_dir}/
install -m 644 %SOURCE3 %{buildroot}%{system_rules_dir}/

install -d %{buildroot}%{_sysconfdir}/sysconfig
install -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/sysconfig/udev

# net rules
install -m 0644 %SOURCE60 %{buildroot}%{system_rules_dir}/
install -m 0755 %SOURCE62 %{buildroot}%{lib_udev_dir}/net_create_ifcfg
install -m 0755 %SOURCE63 %{buildroot}%{lib_udev_dir}/net_action
install -m 0644 %SOURCE64 %{buildroot}/etc/sysconfig/udev_net

mkdir -p %{buildroot}%{_sbindir}
install -m 0755 %SOURCE34 %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/agents.d/usb

touch $RPM_BUILD_ROOT%{_sysconfdir}/scsi_id.config

%{buildroot}%{_sbindir}/udev_import_usermap --no-driver-agent usb %{SOURCE40} %{SOURCE41} > %{buildroot}%{system_rules_dir}/70-hotplug_map.rules

mkdir -p %{buildroot}%{_initrddir}
install -m 0755 udev-post.init %{buildroot}%{_initrddir}/udev-post

%if %{_with_systemd}
# (bor) screen initscript from systemd
ln -s udev-settle.service %{buildroot}/lib/systemd/system/udev-post.service
%endif

# (blino) usb_id are used by drakx
ln -s ..%{lib_udev_dir}/usb_id %{buildroot}/sbin/

# udev rules for zte 3g modems and drakx-net
install -m 0644 %SOURCE66 %{buildroot}%{system_rules_dir}/

mkdir -p %{buildroot}/lib/firmware

rm -rf $RPM_BUILD_ROOT%{_docdir}/udev
rm -f $RPM_BUILD_ROOT/%{_libdir}/*.la

# default /dev content, from Fedora RPM
mkdir -p %{buildroot}%{lib_udev_dir}/devices/{net,hugepages,pts,shm}

# From previous Mandriva /etc/udev/devices.d
mkdir -p %{buildroot}%{lib_udev_dir}/devices/cpu/0

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
perl -n -e '/^\s*device=(.*)/ and symlink($1, "/lib/udev/devices/mouse")' /etc/sysconfig/mouse

%triggerpostun -- udev < 126-1mdv2008.0
# make Mandriva rules compatible with upstream write_cd_rules helper
sed -i -e 's/ENV{MDV_CONFIGURED}="yes"/ENV{GENERATED}="1"/' /etc/udev/rules.d/61-block_config.rules
# set $1 so that udev-post is handled like for a new install
set 1
%_post_service udev-post

%triggerun -- udev <= 164-1mnb2
# migrate from create_static_dev_nodes
for i in /etc/udev/devices.d/*.nodes; do
	[ -e "$i" ] && /sbin/create_static_dev_nodes /lib/udev/devices "$i" || :
done

%files
%defattr(0644,root,root,0755)
%attr(0755,root,root) /sbin/udevadm
%attr(0755,root,root) /sbin/udevd
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
%attr(0755,root,root) %{lib_udev_dir}/mtd_probe
%attr(0755,root,root) /sbin/usb_id
# Default static nodes to copy to /dev on udevd start
%dir %{lib_udev_dir}/devices
# From Fedora RPM
%attr(0755,root,root) %dir	      %{lib_udev_dir}/devices/net
%attr(0755,root,root) %dir	      %{lib_udev_dir}/devices/hugepages
%attr(0755,root,root) %dir	      %{lib_udev_dir}/devices/pts
%attr(0755,root,root) %dir	      %{lib_udev_dir}/devices/shm
%attr(666,root,root) %dev(c,10,200)   %{lib_udev_dir}/devices/net/tun  
%attr(600,root,root) %dev(c,108,0)    %{lib_udev_dir}/devices/ppp  
%attr(666,root,root) %dev(c,10,229)   %{lib_udev_dir}/devices/fuse
%attr(660,root,lp)   %dev(c,6,0)      %{lib_udev_dir}/devices/lp0  
%attr(660,root,lp)   %dev(c,6,1)      %{lib_udev_dir}/devices/lp1
%attr(660,root,lp)   %dev(c,6,2)      %{lib_udev_dir}/devices/lp2  
%attr(660,root,lp)   %dev(c,6,3)      %{lib_udev_dir}/devices/lp3
%attr(640,root,disk) %dev(b,7,0)      %{lib_udev_dir}/devices/loop0
%attr(640,root,disk) %dev(b,7,1)      %{lib_udev_dir}/devices/loop1
%attr(640,root,disk) %dev(b,7,2)      %{lib_udev_dir}/devices/loop2
%attr(640,root,disk) %dev(b,7,3)      %{lib_udev_dir}/devices/loop3
%attr(640,root,disk) %dev(b,7,4)      %{lib_udev_dir}/devices/loop4
%attr(640,root,disk) %dev(b,7,5)      %{lib_udev_dir}/devices/loop5
%attr(640,root,disk) %dev(b,7,6)      %{lib_udev_dir}/devices/loop6
%attr(640,root,disk) %dev(b,7,7)      %{lib_udev_dir}/devices/loop7

# From previous Mandriva /etc/udev/devices.d and patches
%attr(0666,root,root) %dev(c,1,3)     %{lib_udev_dir}/devices/null
%attr(0600,root,root) %dev(b,2,0)     %{lib_udev_dir}/devices/fd0
%attr(0600,root,root) %dev(b,2,1)     %{lib_udev_dir}/devices/fd1
%attr(0600,root,root) %dev(c,21,0)    %{lib_udev_dir}/devices/sg0
%attr(0600,root,root) %dev(c,21,1)    %{lib_udev_dir}/devices/sg1
%attr(0600,root,root) %dev(c,9,0)     %{lib_udev_dir}/devices/st0
%attr(0600,root,root) %dev(c,9,1)     %{lib_udev_dir}/devices/st1
%attr(0600,root,root) %dev(c,99,0)    %{lib_udev_dir}/devices/parport0
%dir %{lib_udev_dir}/devices/cpu
%dir %{lib_udev_dir}/devices/cpu/0
%attr(0600,root,root) %dev(c,203,0)   %{lib_udev_dir}/devices/cpu/0/cpuid
%attr(0600,root,root) %dev(c,10,184)  %{lib_udev_dir}/devices/cpu/0/microcode
%attr(0600,root,root) %dev(c,202,0)   %{lib_udev_dir}/devices/cpu/0/msr
%attr(0600,root,root) %dev(c,162,0)   %{lib_udev_dir}/devices/rawctl
%attr(0600,root,root) %dev(c,195,0)   %{lib_udev_dir}/devices/nvidia0
%attr(0600,root,root) %dev(c,195,255) %{lib_udev_dir}/devices/nvidiactl
%if !%{bootstrap}
%attr(0755,root,root) %{lib_udev_dir}/hid2hci
%attr(0755,root,root) %{lib_udev_dir}/pci-db
%attr(0755,root,root) %{lib_udev_dir}/usb-db
%attr(0755,root,root) %{lib_udev_dir}/keymap
%attr(0755,root,root) %{lib_udev_dir}/udev-acl
%attr(0755,root,root) %{lib_udev_dir}/findkeyboards
%attr(0755,root,root) %{lib_udev_dir}/keyboard-force-release.sh
%attr(0755,root,root) %{lib_udev_dir}/mobile-action-modeswitch
%dir %attr(0755,root,root) %{lib_udev_dir}/keymaps
%attr(0755,root,root) %{lib_udev_dir}/keymaps/*
%attr(0644,root,root) %{_prefix}/lib/ConsoleKit/run-seat.d/udev-acl.ck
%endif
%if %{_with_systemd}
/lib/systemd/system/basic.target.wants/udev-retry.service
/lib/systemd/system/basic.target.wants/udev-settle.service
/lib/systemd/system/basic.target.wants/udev.service
/lib/systemd/system/udev-post.service
/lib/systemd/system/udev-retry.service
/lib/systemd/system/udev-settle.service
/lib/systemd/system/udev.service
%endif

%files doc
%defattr(0644,root,root,0755)
%doc COPYING README TODO ChangeLog NEWS extras/keymap/README.keymap.txt

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
/%{_lib}/libgudev-%{gudev_api}.so.%{gudev_major}*
%{_libdir}/girepository-1.0/GUdev-%{gudev_api}.typelib

%files -n %{gudev_libname_devel}
%defattr(0644,root,root,0755)
%doc %{_datadir}/gtk-doc/html/gudev
%{_libdir}/libgudev-%{gudev_api}.so
%{_includedir}/gudev-%{gudev_api}
%{_datadir}/gir-1.0/GUdev-%{gudev_api}.gir
%{_libdir}/pkgconfig/gudev-%{gudev_api}.pc
%endif
