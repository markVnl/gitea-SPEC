# Do not try to package empty debug_package
%global debug_package %{nil}

Name:		gitea
# TODO: enable network during build for =>1.9.0 || go get them before build..
Version:	1.8.3
Release:	1%{?dist}
Summary:	Gitea is a painless self-hosted Git service.

License:	MIT
URL:		https://gitea.io
Source0:	https://github.com/go-gitea/gitea/archive/v%{version}.tar.gz
Source1:	app.ini
Source2:	gitea.service
Source3:	gitea.conf

BuildRequires:	golang >= 1.8
BuildRequires:	go-bindata
BuildRequires:	pam-devel

Requires:	git

%description
Gitea is a painless self-hosted Git service

%prep
%setup -q -c -n %{name}-%{version}

%build
export GOPATH=$(pwd)
mkdir -p src/code.gitea.io/
mv  %{name}-%{version} src/code.gitea.io/gitea
pushd src/code.gitea.io/gitea
# Fix version without git
sed -i 's/\(LDFLAGS\ :=\ -X\ "main.Version=\)\(.*\)/\1%{version}"\ -X\ "main.Tags=\$\(TAGS\)"/' Makefile
#export TAGS="sqlite bindata pam"
export TAGS="bindata pam"
make generate build
popd

%install
# prepare docs
cp src/code.gitea.io/gitea/LICENSE .

rm -rf %{buildroot}
mkdir -p %{buildroot}%{_bindir}
install -m 755 src/code.gitea.io/gitea/gitea %{buildroot}%{_bindir}/%{name}
mkdir -p %{buildroot}%{_datarootdir}/%{name}
install -m 664 src/code.gitea.io/gitea/custom/conf/app.ini.sample \
			%{buildroot}%{_datarootdir}/%{name}/app.ini.sample
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
install -m 660 %{SOURCE1}  %{buildroot}%{_sysconfdir}/%{name}/app.ini
mkdir -p %{buildroot}/%{_unitdir}
install -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
install -m 0664 %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
# Home & Log dir
install -d -m 0755 %{buildroot}%{_sharedstatedir}/%{name}
install -d -m 0755 %{buildroot}%{_localstatedir}/log/%{name}

%clean
rm -rf %{buildroot}


%pre
getent group %{name} > /dev/null || groupadd -r %{name}
getent passwd %{name} > /dev/null || \
	useradd -r -g %{name} -s /bin/bash \
	-d %{_sharedstatedir}/%{name} \
	-c "Gitea git account" %{name}


%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%files
%doc LICENSE
%{_datarootdir}/%{name}/app.ini.sample
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%attr(0664,%{name},%{name}) %config(noreplace) %{_sysconfdir}/%{name}/app.ini
%attr(0755,%{name},%{name}) %dir %{_localstatedir}/log/%{name}
%attr(0755,%{name},%{name}) %dir %{_sharedstatedir}/%{name}


%changelog
* Fri Sep 13 2019 Mark Verlinde <mark.verlinde@gmail.com> 1.8.3-1
- bump to upsteam release 1.8.3
* Mon Sep 03 2018 Mark Verlinde <mark.verlinde@gmail.com> 1.5.1-1
- bump to upsteam release 1.5.1
* Mon Aug 27 2018 Mark Verlinde <mark.verlinde@gmail.com> 1.5.0-2
- do not package empty debug info
* Wed Aug 22 2018 Mark Verlinde <mark.verlinde@gmail.com> 1.5.0-1
- bump to upsteam release 1.5.0
* Mon Aug 20 2018 Mark Verlinde <mark.verlinde@gmail.com> 1.4.3-0.1
- fix directory permissions
- fix typo in gitea.service
* Thu Aug 02 2018 Mark Verlinde <mark.verlinde@gmail.com> 1.4.3-0.1
- First Build
