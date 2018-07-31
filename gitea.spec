Name:		gitea
Version:	1.4.3
Release:	1%{?dist}
Summary:	Gitea is a painless self-hosted Git service.

License:	MIT
URL:		https://gitea.io
Source0:	https://github.com/go-gitea/gitea/archive/v%{version}.tar.gz
Source1:	app.ini
Source2:	gitea.service
#Source3:	gitea.conf

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
cp src/code.gitea.io/gitea/custom/conf/app.ini.sample .

rm -rf %{buildroot}
mkdir -p %{buildroot}/%{_bindir}/%{name}
install -m 755 src/code.gitea.io/gitea/gitea %{buildroot}/%{_bindir}/%{name}/%{name}
mkdir -p %{buildroot}/%{_sysconfdir}/gitea
install -m 640 %{SOURCE1}  %{buildroot}/%{_sysconfdir}/%{name}/app.ini
mkdir -p %{buildroot}/%{_unitdir}
install -m 644 %{SOURCE2} %{buildroot}/%{_unitdir}/gitea.service
install -d -m 0755 %{buildroot}%{_sharedstatedir}/%{name}
#mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
#install -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/%{name}

%clean
rm -rf %{buildroot}


%pre
getent group gitea > /dev/null || groupadd -r gitea
getent passwd gitea > /dev/null || \
	useradd -r -g gitea -s /bin/bash \
	-d %{_sharedstatedir}/%{name} \
	-c "Gitea git account" gitea


%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%files
%doc LICENSE
%doc app.ini.sample
%{_bindir}/%{name}/%{name}
%{_unitdir}/%{name}.service
%attr(0640,gitea,gitea) %config(noreplace) %{_sysconfdir}/%{name}/app.ini
%attr(0755,%{name},%{name}) %dir %{_sharedstatedir}/%{name}


%changelog
