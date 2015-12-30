%define pkg_name skynet
%define pkg_version 0.0.1
%define pkg_release 1

Name: %{pkg_name}
Version: %{pkg_version}
Release: %{pkg_release}%{?dist}
BuildArch: noarch
Summary: Skyring Node Eventing Agent
Source0: %{pkg_name}-%{pkg_version}.tar.gz
License: Apache License, Version 2.0
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{pkg_name}-%{pkg_version}-%{pkg_release}-buildroot
Url: https://github.com/skyrings/skynet

BuildRequires: python-devel
BuildRequires: python-setuptools

Requires: collectd
Requires: libstoraged
Requires: python-daemon
Requires: python-setuptools
Requires: salt-minion >= 2015.5.5
Requires: storaged
Requires: storaged-lvm2

%description
skynet is the node eventing agent for Skyring. Each storage node managed
by Skyring will have this agent running on them. It is a daemon which listens
to dbus signals, filters it, processes it and pushes the filtered signals to
Skyring using saltstack eventing framework. Currently this daemon has capability
to send basic storage related, few node process related and network related events.

%prep
%setup -n %{pkg_name}-%{pkg_version}

%build
python setup.py build

%install
rm -rf $RPM_BUILD_ROOT
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
install -m 755 -d $RPM_BUILD_ROOT/etc/skynet
install -D src/skynetd/conf/skynet.conf.sample $RPM_BUILD_ROOT/etc/skynet/skynet.conf
install -D src/skynetd/conf/skynet-log.conf.sample $RPM_BUILD_ROOT/etc/skynet/skynet-log.conf
install -D systemd-skynetd.service $RPM_BUILD_ROOT/usr/lib/systemd/system/systemd-skynetd.service

%post
dbus-send --system --print-reply --type=method_call --dest=org.storaged.Storaged /org/storaged/Storaged/Manager org.storaged.Storaged.Manager.EnableModules boolean:true
/bin/systemctl restart systemd-skynetd.service >/dev/null 2>&1 || :

%preun

%clean
rm -rf "$RPM_BUILD_ROOT"

%files -f INSTALLED_FILES
%defattr(-,root,root)
%{_sysconfdir}/skynet/
%{_sysconfdir}/skynet/skynet.conf
%{_sysconfdir}/skynet/skynet-log.conf
/usr/lib/systemd/system/systemd-skynetd.service

%changelog
* Thu Dec 03 2015 <tjeyasin@redhat.com>
- Initial build.
