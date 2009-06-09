%define url ftp://ftp.kernel.org/pub/linux/utils/kernel/hotplug
%define tarname %{name}-%{version}
%define kernel_dir /usr/src/linux
%define use_dietlibc 0

%define main_major 0

%define libname %mklibname %{name} %{main_major}

%define lib_udev_dir /lib/%{name}
%define system_rules_dir %{lib_udev_dir}/rules.d
%define user_rules_dir %{_sysconfdir}/%{name}/rules.d

%{?_without_dietlibc:	%{expand: %%global use_dietlibc 0}}
%{?_with_dietlibc:		%{expand: %%global use_dietlibc 1}}

%define git_url git://git.kernel.org/pub/scm/linux/hotplug/udev.git

Name: 		udev
Version: 	142
Release: 	%manbo_mkrel 3
License: 	GPLv2
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
# (fc) 140-1mdv put back pam console apply for now
Source65:	95-pam-console.rules

# from upstream git

# from Mandriva
# disable coldplug for storage and device pci 
Patch20:	udev-136-coldplug.patch
# patches from Mandriva on Fedora's start_udev
Patch70:	udev-125-devices_d.patch
Patch71:	udev-142-MAKEDEV.patch
# (fc) 142-1mdv hide mknod error (for existing nodes) in start_udev
Patch72:	udev-142-hide-mknod-errors.patch
Patch73:	udev-137-speedboot.patch

#Conflicts:  devfsd
Conflicts:	sound-scripts < 0.13-1mdk
Conflicts:	hotplug < 2004_09_23-22mdk
Conflicts:	pam < pam-0.99.3.0-1mdk
Conflicts:	initscripts < 8.51-7mdv2007.1
Requires:	coreutils
Requires:	setup >= 2.7.16
Requires:	util-linux-ng >= 2.15
%if %use_dietlibc
BuildRequires:	dietlibc
%endif
BuildRequires:	glibc-static-devel
BuildRequires:  libblkid-devel
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

%prep
%setup -q
%patch20 -p1 -b .coldplug
cp -a %{SOURCE7} .
%patch70 -p1 -b .devices_d
%patch71 -p1 -b .MAKEDEV
%patch72 -p1 -b .hide-mknod-errors
%patch73 -p1 -b .speedboot

%build
%serverbuild
%configure2_5x \
  --prefix=%{_prefix} \
  --exec-prefix="" \
  --sysconfdir=%{_sysconfdir} \
  --with-libdir-name=%{_lib} \
  --sbindir="/sbin" \
  --enable-static

%make

%install
rm -rf %{buildroot}
%make DESTDIR=%{buildroot} install

%if %use_dietlibc
install -d %{buildroot}%{_prefix}/lib/dietlibc/lib-%{_arch}
%endif

install -m 755 start_udev %{buildroot}/sbin/
install -m 755 %SOURCE9 %{buildroot}/sbin/

# extra docs
install -m 644 extras/scsi_id/README README.scsi_id

install -m 644 %SOURCE2 %{buildroot}%{system_rules_dir}/
# use RH rules for pam_console
install -m 644 %SOURCE65 %{buildroot}%{system_rules_dir}/95-pam-console.rules
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

# (blino) usb_id are used by drakx
ln -s ..%{lib_udev_dir}/usb_id %{buildroot}/sbin/

mkdir -p %{buildroot}/lib/firmware

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

