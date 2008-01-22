%define url ftp://ftp.kernel.org/pub/linux/utils/kernel/hotplug
%define tarname %{name}-%{version}
%define kernel_dir /usr/src/linux
%define use_klibc 0
%define use_dietlibc 1

%define volid_name volume_id
%define lib_volid_name %mklibname %{volid_name} 0

%define helpers_path /%{_lib}/%{name}
%define EXTRAS "extras/ata_id extras/cdrom_id extras/edd_id extras/firmware extras/path_id/ extras/scsi_id extras/usb_id extras/volume_id/"

%{?_without_klibc:	%{expand: %%global use_klibc 0}}
%{?_with_klibc:		%{expand: %%global use_klibc 1}}
%{?_without_dietlibc:	%{expand: %%global use_dietlibc 0}}
%{?_with_dietlibc:		%{expand: %%global use_dietlibc 1}}

Name: 		udev
Version: 	118
Release: 	%mkrel 2
License: 	GPL
Summary: 	A userspace implementation of devfs
Group:		System/Configuration/Hardware
URL:		%{url}
Source: 	%{url}/%{tarname}.tar.bz2
Source2:	50-udev-mandriva.rules
Source7:	start_udev
Source8:	default.nodes
Source9:	create_static_dev_nodes
Source34:	udev_import_usermap
# from hotplug-2004_09_23
Source40:	hotplug-usb.distmap
Source41:	hotplug-usb.handmap
# (blino) persistent rules library and utility
Source50:	udev_persistent_lib.sh
Source51:	udev_copy_temp_rules
# (blino) net rules and helpers
Source60:	62-net.rules
Source61:	udev_net_name_helper
Source62:	udev_net_create_ifcfg
Source63:	udev_net_action
Source64:	udev_net.sysconfig
# (blino) persistent block rules
Source70:	62-create_persistent.rules
Source71:	udev_cdrom_helper

# from Mandriva
Patch20:	udev-117-coldplug.patch
# make hardcoded /lib/udev path configurable
Patch50:	udev-114-libudevdir.patch
Patch70:	udev-114-devices_d.patch
Patch71:	udev-109-MAKEDEV.patch

#Conflicts:  devfsd
Conflicts:	sound-scripts < 0.13-1mdk
Conflicts:	hotplug < 2004_09_23-22mdk
Conflicts:	pam < pam-0.99.3.0-1mdk
Conflicts:	initscripts < 8.51-7mdv2007.1
Requires:	coreutils
%if %use_klibc
BuildRequires:	kernel-source
Obsoletes: %{name}-klibc
Provides: %{name}-klibc
%endif
%if %use_dietlibc
BuildRequires:	dietlibc
%endif
BuildRequires:	glibc-static-devel
BuildRequires:	libsysfs-devel
BuildRoot: 	%{_tmppath}/%{name}-%{version}-build
Obsoletes:	speedtouch eagle-usb

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

%package tools
Summary: Udev tools
Group: System/Configuration/Hardware
Conflicts: udev < 068-14mdk
%description tools
This package contains tools to help debugging and monitoring of udev.

%package -n %{lib_volid_name}
Group: System/Libraries
Summary: Library for volume_id
%description -n %{lib_volid_name}
Library for volume_id.

%package -n %{lib_volid_name}-devel
Group: Development/C
Summary: Devel library for volume_id
Provides: %{volid_name}-devel = %{version}-%{release}
Provides: lib%{volid_name}-devel = %{version}-%{release}
Requires: %{lib_volid_name} = %{version}
%description -n %{lib_volid_name}-devel
Devel library for volume_id.

%prep
%setup -q
# help vi/gendiff:
find -type f | xargs chmod u+rw
%patch20 -p1 -b .coldplug
%patch50 -p1 -b .libudevdir
cp -a %{SOURCE7} .
%patch70 -p1 -b .devices_d
%patch71 -p1 -b .MAKEDEV

perl -pi -e "s@/lib/udev@%{helpers_path}@" README RELEASE-NOTES

%build
%serverbuild
%if %use_klibc
make KERNEL_DIR=%{kernel_dir} LINUX_INCLUDE_DIR=%{_includedir} USE_KLIBC=true USE_LOG=false libudevdir=/%{_lib}/udev
install -m 755 udev udev-klibc 
%make clean
%endif

%if %use_dietlibc
make E=@\# CC="diet gcc" CFLAGS="-Os" RANLIB="ranlib" -C extras/volume_id/lib libvolume_id.a
mv extras/volume_id/lib/libvolume_id.a libvolume_id.a.diet
%make clean
%endif

make libudevdir=/%{_lib}/udev EXTRAS=%EXTRAS USE_LOG=true

%install
rm -rf $RPM_BUILD_ROOT
%make EXTRAS=%EXTRAS DESTDIR=$RPM_BUILD_ROOT install libudevdir=/%{_lib}/udev libdir=/%{_lib} usrlibdir=%{_libdir}

%if %use_klibc
install -m 755 udev-klibc $RPM_BUILD_ROOT/sbin/
%endif

%if %use_dietlibc
install -d $RPM_BUILD_ROOT%{_prefix}/lib/dietlibc/lib-%{_arch}
install libvolume_id.a.diet $RPM_BUILD_ROOT%{_prefix}/lib/dietlibc/lib-%{_arch}/libvolume_id.a
%endif

install -m 755 start_udev $RPM_BUILD_ROOT/sbin/
install -m 755 %SOURCE9 $RPM_BUILD_ROOT/sbin/

# extra docs
install -m 644 extras/scsi_id/README README.scsi_id
install -m 644 extras/volume_id/README README.udev_volume_id

install -m 644 %SOURCE2 $RPM_BUILD_ROOT/etc/%{name}/rules.d/
install -m 644 etc/%{name}/rules.d/*.rules $RPM_BUILD_ROOT/etc/%{name}/rules.d/
# 40-suse contains rules to set video group
install -m 644 etc/%{name}/suse/40-suse.rules $RPM_BUILD_ROOT/etc/%{name}/rules.d/40-video.rules
# use RH rules for pam_console
install -m 644 etc/%{name}/redhat/95-pam-console.rules $RPM_BUILD_ROOT/etc/%{name}/rules.d/95-pam-console.rules
# use upstream rules for sound devices, device mapper, raid devices
for f in \
  40-alsa \
  64-device-mapper \
  64-md-raid \
  ; do
    install -m 644 etc/%{name}/packages/$f.rules $RPM_BUILD_ROOT/etc/%{name}/rules.d/
done

# persistent lib
install -m 0755 %SOURCE50 $RPM_BUILD_ROOT%{helpers_path}
# copy temp rules
install -m 0755 %SOURCE51 $RPM_BUILD_ROOT/sbin/
# net rules
install -m 0644 %SOURCE60 $RPM_BUILD_ROOT/etc/%{name}/rules.d/
install -m 0755 %SOURCE61 $RPM_BUILD_ROOT%{helpers_path}/net_name_helper
install -m 0755 %SOURCE62 $RPM_BUILD_ROOT%{helpers_path}/net_create_ifcfg
install -m 0755 %SOURCE63 $RPM_BUILD_ROOT%{helpers_path}/net_action
install -D -m 0644 %SOURCE64 $RPM_BUILD_ROOT/etc/sysconfig/udev_net
# persistent block
install -m 0644 %SOURCE70 $RPM_BUILD_ROOT/etc/%{name}/rules.d/
install -m 0755 %SOURCE71 $RPM_BUILD_ROOT%{helpers_path}/cdrom_helper

mkdir -p $RPM_BUILD_ROOT/%_sysconfdir/udev/devices.d/
install -m 0755 %SOURCE8 $RPM_BUILD_ROOT/%_sysconfdir/udev/devices.d/

install -m 0755 %SOURCE34 $RPM_BUILD_ROOT%{_sbindir}
mkdir -p $RPM_BUILD_ROOT/%_sysconfdir/udev/agents.d/usb

$RPM_BUILD_ROOT%{_sbindir}/udev_import_usermap --no-driver-agent usb %{SOURCE40} %{SOURCE41} > $RPM_BUILD_ROOT/etc/udev/rules.d/70-hotplug_map.rules

# (blino) usb_id/vol_id are used by drakx
ln -s ..%{helpers_path}/usb_id $RPM_BUILD_ROOT/sbin/
ln -s ..%{helpers_path}/vol_id $RPM_BUILD_ROOT/sbin/

# (bluca, tv, blino) fix agent and library path on x86_64
perl -pi -e "s@/lib/udev@%{helpers_path}@" \
     $RPM_BUILD_ROOT/sbin/start_udev \
     $RPM_BUILD_ROOT/sbin/udev_copy_temp_rules \
     $RPM_BUILD_ROOT%{helpers_path}/* \
     $RPM_BUILD_ROOT/etc/%{name}/rules.d/*

mkdir -p $RPM_BUILD_ROOT/lib/firmware

%check
%if %{_lib} != lib
find $RPM_BUILD_ROOT \
     -not -wholename '*/usr/*/debug/*' -a \
     -not -wholename '*/usr/share/doc/*' -a \
     -not -wholename '*/usr/share/man/*' \
     -print0 \
     | xargs -0 grep /lib/udev && exit 1
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n %{lib_volid_name} -p /sbin/ldconfig
%postun -n %{lib_volid_name} -p /sbin/ldconfig

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

%files
%defattr(0644,root,root,0755)
%attr(0755,root,root) /sbin/udevadm
%attr(0755,root,root) /sbin/udevcontrol
%attr(0755,root,root) /sbin/udevd
%attr(0755,root,root) /sbin/udevsettle
%attr(0755,root,root) /sbin/udevtrigger
%attr(0755,root,root) /sbin/udev_copy_temp_rules
%attr(0755,root,root) /sbin/create_static_dev_nodes
%attr(0755,root,root) /sbin/start_udev
%attr(0755,root,root) %{_bindir}/udevinfo
%dir %_sysconfdir/udev/agents.d
%dir %_sysconfdir/udev/agents.d/usb
%config(noreplace) %{_sysconfdir}/sysconfig/udev_net
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%config(noreplace) %{_sysconfdir}/scsi_id.config
%{_sysconfdir}/%{name}/rules.d/*
%dir %{_sysconfdir}/udev
%dir %{_sysconfdir}/udev/rules.d
%dir %{_sysconfdir}/%{name}/devices.d
%config(noreplace) %{_sysconfdir}/%{name}/devices.d/*.nodes
%_mandir/man7/*
%_mandir/man8/*
%exclude %_mandir/man8/udevtest*
%exclude %_mandir/man8/udevmonitor*
%dir /lib/firmware
%dir %{helpers_path}
%attr(0755,root,root) %{helpers_path}/ata_id
%attr(0755,root,root) %{helpers_path}/cdrom_id
%attr(0755,root,root) %{helpers_path}/edd_id
%attr(0755,root,root) %{helpers_path}/path_id
%attr(0755,root,root) %{helpers_path}/scsi_id
%attr(0755,root,root) %{helpers_path}/usb_id
%attr(0755,root,root) %{helpers_path}/vol_id
%attr(0755,root,root) %{helpers_path}/firmware.sh
%attr(0755,root,root) %{helpers_path}/cdrom_helper
%attr(0755,root,root) %{helpers_path}/udev_persistent_lib.sh
%attr(0755,root,root) %{helpers_path}/net_create_ifcfg
%attr(0755,root,root) %{helpers_path}/net_action
%attr(0755,root,root) %{helpers_path}/net_name_helper
%attr(0755,root,root) /sbin/usb_id
%attr(0755,root,root) /sbin/vol_id

%if %use_klibc
%attr(0755,root,root) /sbin/*-klibc
%endif

%files doc
%defattr(0644,root,root,0755)
%doc COPYING README README.* TODO ChangeLog RELEASE-NOTES
%doc docs/overview docs/udev_vs_devfs
%doc docs/writing_udev_rules/*

%files tools
%defattr(0644,root,root,0755)
%attr(0755,root,root) %{_bindir}/udevtest
%attr(0755,root,root) %{_sbindir}/udevmonitor
%attr(0755,root,root) %{_sbindir}/udev_import_usermap
%_mandir/man8/udevtest*
%_mandir/man8/udevmonitor*

%files -n %{lib_volid_name}
/%{_lib}/lib%{volid_name}.so.*

%files -n %{lib_volid_name}-devel
%{_libdir}/lib%{volid_name}.*
%if %use_dietlibc
%{_prefix}/lib/dietlibc/lib-%{_arch}/libvolume_id.a
%endif
%{_libdir}/pkgconfig/lib%{volid_name}.pc
%{_includedir}/lib%{volid_name}.h

