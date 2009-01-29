%define url ftp://ftp.kernel.org/pub/linux/utils/kernel/hotplug
%define tarname %{name}-%{version}
%define kernel_dir /usr/src/linux
%define use_klibc 0
%define use_dietlibc 0

%define main_major 0
%define volid_major 1

%define libname %mklibname %{name} %{main_major}
%define volid_name volume_id
%define lib_volid_name %mklibname %{volid_name} %{volid_major}

%define lib_udev_dir /lib/%{name}
%define system_rules_dir %{lib_udev_dir}/rules.d
%define user_rules_dir %{_sysconfdir}/%{name}/rules.d

%{?_without_klibc:	%{expand: %%global use_klibc 0}}
%{?_with_klibc:		%{expand: %%global use_klibc 1}}
%{?_without_dietlibc:	%{expand: %%global use_dietlibc 0}}
%{?_with_dietlibc:		%{expand: %%global use_dietlibc 1}}

Name: 		udev
Version: 	137
Release: 	%manbo_mkrel 1
License: 	GPL
Summary: 	A userspace implementation of devfs
Group:		System/Configuration/Hardware
URL:		%{url}
Source: 	%{url}/%{tarname}.tar.bz2
Source2:	50-udev-mandriva.rules
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

# from upstream git

# from Mandriva
# disable coldplug for storage and device pci 
Patch20:	udev-136-coldplug.patch
Patch21:	udev-128-lseek64.patch
# (fc) create by-id symlink for pure HID devices
Patch22:	udev-131-hiddevice.patch
# patches from Mandriva on Fedora's start_udev
Patch70:	udev-125-devices_d.patch
Patch71:	udev-136-MAKEDEV.patch
Patch72:	udev-136-restorecon.patch

#Conflicts:  devfsd
Conflicts:	sound-scripts < 0.13-1mdk
Conflicts:	hotplug < 2004_09_23-22mdk
Conflicts:	pam < pam-0.99.3.0-1mdk
Conflicts:	initscripts < 8.51-7mdv2007.1
Requires:	coreutils
Requires:	setup >= 2.7.16
%if %use_klibc
BuildRequires:	kernel-source
Obsoletes: %{name}-klibc
Provides: %{name}-klibc
%endif
%if %use_dietlibc
BuildRequires:	dietlibc
%endif
BuildRequires:	glibc-static-devel
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
%description -n %{libname}
Library for %{name}.

%package -n %{libname}-devel
Group: Development/C
Summary: Devel library for %{name}
Provides: %{name}-devel = %{version}-%{release}
Provides: lib%{name}-devel = %{version}-%{release}
Requires: %{libname} = %{version}
%description -n %{libname}-devel
Devel library for %{udev}.

%package -n %{lib_volid_name}
Group: System/Libraries
Summary: Library for %{volid_name}
%description -n %{lib_volid_name}
Library for %{volid_name}.

%package -n %{lib_volid_name}-devel
Group: Development/C
Summary: Devel library for %{volid_name}
Provides: %{volid_name}-devel = %{version}-%{release}
Provides: lib%{volid_name}-devel = %{version}-%{release}
Requires: %{lib_volid_name} = %{version}
%description -n %{lib_volid_name}-devel
Devel library for %{volid_name}.

%prep
%setup -q
# help vi/gendiff:
find -type f | xargs chmod u+rw
%patch20 -p1 -b .coldplug
%patch21 -p1 -b .lseek64
%patch22 -p1 -b .hiddevice
cp -a %{SOURCE7} .
%patch70 -p1 -b .devices_d
%patch71 -p1 -b .MAKEDEV
%patch72 -p1 -b .restorecon

%build
%serverbuild
%configure2_5x \
  --prefix=%{_prefix} \
  --exec-prefix="" \
  --sysconfdir=%{_sysconfdir} \
  --with-libdir-name=%{_lib} \
  --sbindir="/sbin" \
  --enable-static

%if %use_klibc
%make KERNEL_DIR=%{kernel_dir} LINUX_INCLUDE_DIR=%{_includedir} USE_KLIBC=true
install -m 755 udev udev-klibc 
%make clean
%endif

%if %use_dietlibc
%make E=@\# CC="diet gcc" CFLAGS="-Os" RANLIB="ranlib" -C extras/%{volid_name}/lib lib%{volid_name}.la
mv extras/%{volid_name}/lib/.libs/lib%{volid_name}.a lib%{volid_name}.a.diet
%make clean
%endif

%make

%install
rm -rf %{buildroot}
%make DESTDIR=%{buildroot} install

%if %use_klibc
install -m 755 udev-klibc %{buildroot}/sbin/
%endif

%if %use_dietlibc
install -d %{buildroot}%{_prefix}/lib/dietlibc/lib-%{_arch}
install lib%{volid_name}.a.diet %{buildroot}%{_prefix}/lib/dietlibc/lib-%{_arch}/lib%{volid_name}.a
%endif

install -m 755 start_udev %{buildroot}/sbin/
install -m 755 %SOURCE9 %{buildroot}/sbin/

# extra docs
install -m 644 extras/scsi_id/README README.scsi_id
install -m 644 extras/%{volid_name}/README README.udev_%{volid_name}

install -m 644 %SOURCE2 %{buildroot}%{system_rules_dir}/
# use RH rules for pam_console
install -m 644 rules/redhat/95-pam-console.rules %{buildroot}%{system_rules_dir}/95-pam-console.rules
# use upstream rules for sound devices, device mapper, raid devices
for f in \
  40-alsa \
  64-device-mapper \
  64-md-raid \
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

%{buildroot}%{_sbindir}/udev_import_usermap --no-driver-agent usb %{SOURCE40} %{SOURCE41} > %{buildroot}%{system_rules_dir}/70-hotplug_map.rules

mkdir -p %{buildroot}%{_initrddir}
install -m 0755 %{SOURCE6} %{buildroot}%{_initrddir}/udev-post

# (blino) usb_id/vol_id are used by drakx
ln -s ..%{lib_udev_dir}/usb_id %{buildroot}/sbin/
ln -s ..%{lib_udev_dir}/vol_id %{buildroot}/sbin/

mkdir -p %{buildroot}/lib/firmware

%clean
rm -rf %{buildroot}

%post
%_post_service udev-post

%preun
%_preun_service udev-post

%if %mdkversion < 200900
%post -n %{lib_volid_name} -p /sbin/ldconfig
%endif
%if %mdkversion < 200900
%postun -n %{lib_volid_name} -p /sbin/ldconfig
%endif

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
%config(noreplace) %{_sysconfdir}/scsi_id.config
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
%attr(0755,root,root) %{lib_udev_dir}/path_id
%attr(0755,root,root) %{lib_udev_dir}/scsi_id
%attr(0755,root,root) %{lib_udev_dir}/usb_id
%attr(0755,root,root) %{lib_udev_dir}/vol_id
%attr(0755,root,root) %{lib_udev_dir}/collect
%attr(0755,root,root) %{lib_udev_dir}/create_floppy_devices
%attr(0755,root,root) %{lib_udev_dir}/firmware.sh
%attr(0755,root,root) %{lib_udev_dir}/fstab_import
%attr(0755,root,root) %{lib_udev_dir}/rule_generator.functions
%attr(0755,root,root) %{lib_udev_dir}/write_cd_rules
%attr(0755,root,root) %{lib_udev_dir}/write_net_rules
%attr(0755,root,root) %{lib_udev_dir}/net_create_ifcfg
%attr(0755,root,root) %{lib_udev_dir}/net_action
%attr(0755,root,root) /sbin/usb_id
%attr(0755,root,root) /sbin/vol_id

%if %use_klibc
%attr(0755,root,root) /sbin/*-klibc
%endif

%files doc
%defattr(0644,root,root,0755)
%doc COPYING README README.* TODO ChangeLog NEWS
%doc docs/writing_udev_rules/*

%files -n %{libname}
/%{_lib}/lib%{name}.so.%{main_major}
/%{_lib}/lib%{name}.so.%{main_major}.*

%files -n %{libname}-devel
%{_libdir}/lib%{name}.*
%if %use_dietlibc
%{_prefix}/lib/dietlibc/lib-%{_arch}/lib%{name}.a
%endif
%{_libdir}/pkgconfig/lib%{name}.pc
%{_includedir}/lib%{name}.h

%files -n %{lib_volid_name}
/%{_lib}/lib%{volid_name}.so.%{volid_major}
/%{_lib}/lib%{volid_name}.so.%{volid_major}.*

%files -n %{lib_volid_name}-devel
%{_libdir}/lib%{volid_name}.*
%if %use_dietlibc
%{_prefix}/lib/dietlibc/lib-%{_arch}/lib%{volid_name}.a
%endif
%{_libdir}/pkgconfig/lib%{volid_name}.pc
%{_includedir}/lib%{volid_name}.h

