Summary: High-performance and highly configurable RADIUS server
URL: http://www.freeradius.org/
Name: freeradius
Version: 0.6
Release: 1
License: GPL
Group: Networking/Daemons
Packager: FreeRADIUS.org
Source0: %{name}-%{version}.tar.gz
Prereq: /sbin/chkconfig
BuildPreReq: libtool
# FIXME: snmpwalk, snmpget and rusers POSSIBLY needed by checkrad
Conflicts: cistron-radius
BuildRoot: %{_tmppath}/%{name}-root

%description
The FreeRADIUS Server Project is a high-performance and highly
configurable GPL'd RADIUS server. It is somewhat similar to the
Livingston 2.0 RADIUS server, but has many more features, and is much
more configurable.

%prep 
%setup

%build
CFLAGS="$RPM_OPT_FLAGS" \
%configure --prefix=%{_prefix} \
	--localstatedir=%{_localstatedir} \
	--sysconfdir=%{_sysconfdir} \
	--mandir=%{_mandir} \
	--with-threads \
	--with-thread-pool \
	--with-gnu-ld \
	--disable-ltdl-install \
	--with-rlm-sql_postgresql-include-dir=/usr/include/pgsql \
	--with-rlm-krb5-include-dir=/usr/kerberos/include \
	--with-rlm-krb5-lib-dir=/usr/kerberos/lib
make

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/etc/{logrotate.d,pam.d,rc.d/init.d}

make install R=$RPM_BUILD_ROOT

# set radiusd as default user/group
sed -e 's/^user =.*$/user = radiusd/' -e 's/^group =.*$/group = radiusd/' < $RPM_BUILD_ROOT/etc/raddb/radiusd.conf > $RPM_BUILD_ROOT/radiusd.conf.tmp
mv $RPM_BUILD_ROOT/radiusd.conf.tmp $RPM_BUILD_ROOT/etc/raddb/radiusd.conf

# shadow password file MUST be defined on Linux
sed -e 's/#	shadow =/shadow =/' < $RPM_BUILD_ROOT/etc/raddb/radiusd.conf > $RPM_BUILD_ROOT/radiusd.conf.tmp
mv $RPM_BUILD_ROOT/radiusd.conf.tmp $RPM_BUILD_ROOT/etc/raddb/radiusd.conf

# remove unneeded stuff
rm -f $RPM_BUILD_ROOT%{_mandir}/man8/builddbm.8
rm -f $RPM_BUILD_ROOT%{_prefix}/sbin/rc.radiusd

cd redhat
install -m 755 rc.radiusd-redhat $RPM_BUILD_ROOT/etc/rc.d/init.d/radiusd
install -m 644 radiusd-logrotate $RPM_BUILD_ROOT/etc/logrotate.d/radiusd
install -m 644 radiusd-pam       $RPM_BUILD_ROOT/etc/pam.d/radius
cd ..

%pre
/usr/sbin/useradd -c "radiusd user" -r -s /bin/false -u 95 -d / radiusd 2>/dev/null || :

%preun
if [ "$1" = "0" ]; then
	/sbin/service radiusd stop > /dev/null 2>&1
	/sbin/chkconfig --del radiusd
fi

%post
/sbin/ldconfig
/sbin/chkconfig --add radiusd

# Done here to avoid messing up existing installations
for i in radius/radutmp radius/radwtmp radius/radius.log # radius/radwatch.log radius/checkrad.log
do
	touch /var/log/$i
	chown radiusd:radiusd /var/log/$i
	chmod 600 /var/log/$i
done

%postun
if [ "$1" -ge "1" ]; then
	/sbin/service radiusd condrestart >/dev/null 2>&1
fi
if [ $1 = 0 ]; then
	/usr/sbin/userdel radiusd > /dev/null 2>&1 || :
fi
/sbin/ldconfig

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc doc/ChangeLog doc/README* todo/ COPYRIGHT INSTALL
%config /etc/pam.d/radius
%config /etc/logrotate.d/radiusd
%config /etc/rc.d/init.d/radiusd
%config (noreplace) /etc/raddb/[a-ce-z]*
%config /etc/raddb/d*
%{_mandir}/*/*
/usr/bin/*
/usr/sbin/*
/usr/lib/*
%attr(0700,radiusd,radiusd) %dir /var/log/radius
%attr(0700,radiusd,radiusd) %dir /var/log/radius/radacct
%attr(0700,radiusd,radiusd) %dir /var/run/radiusd

%changelog
* Tue Jun 18 2002 Marko Myllynen
- run as radiusd user instead of root
- added some options for configure

* Thu Jun  6 2002 Marko Myllynen
- set noreplace for non-dictionary files in /etc/raddb

* Sun May 26 2002 Frank Cusack <frank@google.com>
- move /var dirs from %%post to %%files

* Thu Feb 14 2002 Marko Myllynen
- use dir name macros in all configure options
- libtool is required only when building the package
- misc clean ups

* Wed Feb 13 2002 Marko Myllynen
- use %%{_mandir} instead of /usr/man
- rename %%postin as %%post
- clean up name/version

* Fri Jan 18 2002 Frank Cusack <frank@google.com>
- remove (noreplace) for /etc/raddb/* (due to rpm bugs)

* Fri Sep 07 2001 Ivan F. Martinez <ivanfm@ecodigit.com.br>
- changes to make compatible with default config file shipped
- adjusts log files are on /var/log/radius instead of /var/log
- /etc/raddb changed to config(noreplace) to don't override
-   user configs

* Fri Sep 22 2000 Bruno Lopes F. Cabral <bruno@openline.com.br>
- spec file clear accordling to the libltdl fix and minor updates

* Wed Sep 12 2000 Bruno Lopes F. Cabral <bruno@openline.com.br>
- Updated to snapshot-12-Sep-00

* Fri Jun 16 2000 Bruno Lopes F. Cabral <bruno@openline.com.br>
- Initial release
