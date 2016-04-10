%define pkg_name skynet
%define pkg_version 0.0.1
%define pkg_release 1

Name: %{pkg_name}
Version: %{pkg_version}
Release: %{pkg_release}%{?dist}
BuildArch: noarch
Summary: SKYRING Node Event Agent
Source0: %{pkg_name}-%{pkg_version}.tar.gz
License: ASL 2.0
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{pkg_name}-%{pkg_version}-%{pkg_release}-buildroot
Url: https://github.com/skyrings/skynet

BuildRequires: python-devel
BuildRequires: python-setuptools

Requires: collectd
Requires: collectd-ping
Requires: python-cpopen
Requires: python-daemon
Requires: python-setuptools
Requires: salt-minion >= 2015.5.5
Requires: storaged
Requires: storaged-lvm2

%description
SKYNET is the event agent for SKYRING. Each storage node managed
by SKYRING will have this agent running on them. It is a daemon which listens
to DBUS signals, filters it, processes it and pushes the filtered signals to
SKYRING using salt-stack event framework. Currently this daemon has
capability to send basic storage, process and network related events.

%prep
%setup -n %{pkg_name}-%{pkg_version}

%build
python setup.py build

%install
rm -rf $RPM_BUILD_ROOT
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
install -Dm 0644 src/skynetd/conf/skynet.conf.sample $RPM_BUILD_ROOT/etc/skynet/skynet.conf
install -Dm 0644 src/skynetd/conf/skynet-log.conf.sample $RPM_BUILD_ROOT/etc/skynet/skynet-log.conf
install -Dm 0644 systemd-skynetd.service $RPM_BUILD_ROOT/usr/lib/systemd/system/systemd-skynetd.service
install -D src/collectd_scripts/handle_collectd_notification.py $RPM_BUILD_ROOT/usr/lib64/collectd/handle_collectd_notification.py
gzip skynetd.8
install -Dm 0644 skynetd.8.gz $RPM_BUILD_ROOT%{_mandir}/man8/skynetd.8.gz
chmod a+x $RPM_BUILD_ROOT%{python_sitelib}/skynetd/skynetd.py

%pre
if [ `grep -c ^skyring-user /etc/passwd` = "0" ]; then
    /usr/sbin/useradd skyring-user -g wheel
fi

%post
dbus-send --system --print-reply --type=method_call --dest=org.storaged.Storaged /org/storaged/Storaged/Manager org.storaged.Storaged.Manager.EnableModules boolean:true
/bin/systemctl restart systemd-skynetd.service >/dev/null 2>&1 || :
if [ `grep -c ^skyring-user /etc/sudoers` = "0" ]; then
    echo "skyring-user ALL=(ALL) NOPASSWD:ALL" | (EDITOR="tee -a" visudo)
fi

%clean
rm -rf "$RPM_BUILD_ROOT"

%files -f INSTALLED_FILES
%defattr(-,root,root)
%{_sysconfdir}/skynet/
%config(noreplace) %{_sysconfdir}/skynet/skynet.conf
%config(noreplace) %{_sysconfdir}/skynet/skynet-log.conf
%{_usr}/lib/systemd/system/systemd-skynetd.service
%{_usr}/lib64/collectd/
%doc README.md
%{_mandir}/man8/skynetd.8*

%changelog
* Thu Dec 03 2015 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 0.0.1-1
- Initial build.
