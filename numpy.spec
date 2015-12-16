%{?scl:%scl_package numpy}
%{!?scl:%global pkg_name %{name}}

#%{!?python_sitearch: %global python_sitearch %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

#uncomment next line for a release candidate or a beta
#global relc rc1

Name:           %{?scl_prefix}numpy
Version:        1.8.2
Release:        1%{?dist}
Epoch:          1
Summary:        A fast multidimensional array facility for Python

Group:          Development/Languages
# Everything is BSD except for class SafeEval in numpy/lib/utils.py which is Python
License:        BSD and Python
URL:            http://www.numpy.org/
Source0:        http://downloads.sourceforge.net/numpy/%{pkg_name}-%{version}%{?relc}.tar.gz

BuildRequires:  %{?scl_prefix}python-devel lapack-devel %{?scl_prefix}python-setuptools gcc-gfortran atlas-devel %{?scl_prefix}python-nose
Requires:       %{?scl_prefix}python-nose
#BuildRequires:  Cython

%description
NumPy is a general-purpose array-processing package designed to
efficiently manipulate large multi-dimensional arrays of arbitrary
records without sacrificing too much speed for small multi-dimensional
arrays.  NumPy is built on the Numeric code base and adds features
introduced by numarray as well as an extended C-API and the ability to
create arrays of arbitrary type.

There are also basic facilities for discrete fourier transform,
basic linear algebra and random number generation. Also included in
this package is a version of f2py that works properly with NumPy.

%package f2py
Summary:        f2py for numpy
Group:          Development/Libraries
Requires:       %{?scl_prefix}%{pkg_name} = %{epoch}:%{version}-%{release}
Requires:       %{?scl_prefix}python-devel
Provides:       %{?scl_prefix}f2py = %{version}-%{release}
Obsoletes:      %{?scl_prefix}f2py <= 2.45.241_1927

%description f2py
This package includes a version of f2py that works properly with NumPy.

%prep
%setup -q -n %{pkg_name}-%{version}%{?relc}
# workaround for rhbz#849713
# http://mail.scipy.org/pipermail/numpy-discussion/2012-July/063530.html
rm numpy/distutils/command/__init__.py && touch numpy/distutils/command/__init__.py

cat >> site.cfg <<EOF
[DEFAULT]
library_dirs = %{?scl:%_root_libdir}%{?!scl:%_libdir}
include_dirs = %{?scl:%_root_includedir}%{?!scl:%_includedir}
[atlas]
library_dirs = %{?scl:%_root_libdir}%{?!scl:%_libdir}/atlas
atlas_libs = tatlas
EOF

%build
%{?scl:scl enable %{scl} - << \EOF}
env ATLAS=%{?scl:%_root_libdir}%{?!scl:%_libdir} \
    FFTW=%{?scl:%_root_libdir}%{?!scl:%_libdir} \
    BLAS=%{?scl:%_root_libdir}%{?!scl:%_libdir} \
    LAPACK=%{?scl:%_root_libdir}%{?!scl:%_libdir} \
    CFLAGS="%{optflags}" \
    %{__python3} setup.py build
%{?scl:EOF}

%install

#%%{__python} setup.py install -O1 --skip-build --root %%{buildroot}
# skip-build currently broken, this works around it for now

%{?scl:scl enable %{scl} - << \EOF}
env ATLAS=%{?scl:%_root_libdir}%{?!scl:%_libdir} \
    FFTW=%{?scl:%_root_libdir}%{?!scl:%_libdir} \
    BLAS=%{?scl:%_root_libdir}%{?!scl:%_libdir} \
    LAPACK=%{?scl:%_root_libdir}%{?!scl:%_libdir} \
    CFLAGS="%{optflags}" \
    %{__python3} setup.py install --root %{buildroot}
%{?scl:EOF}

rm -rf docs-f2py ; mv %{buildroot}%{python3_sitearch}/%{pkg_name}/f2py/docs docs-f2py
mv -f %{buildroot}%{python3_sitearch}/%{pkg_name}/f2py/f2py.1 f2py.1
# save dir for tests, remove sphinx docs
rm -rf doc/*
install -D -p -m 0644 f2py.1 %{buildroot}%{_mandir}/man1/f2py.1

pushd %{buildroot}%{_bindir} &> /dev/null

# resolves rhbz#1053011
sed -i -e 's"^#!/usr/bin/env python"#!%{?_scl_root}/usr/bin/python"' f2py3

popd &> /dev/null

#symlink for includes, BZ 185079
mkdir -p %{buildroot}%{_includedir}
ln -s %{python3_sitearch}/%{pkg_name}/core/include/numpy/ %{buildroot}%{_includedir}/numpy

# Remove doc files. They should in in %%doc
rm -f %{buildroot}%{python3_sitearch}/%{pkg_name}/COMPATIBILITY
rm -f %{buildroot}%{python3_sitearch}/%{pkg_name}/DEV_README.txt
rm -f %{buildroot}%{python3_sitearch}/%{pkg_name}/INSTALL.txt
rm -f %{buildroot}%{python3_sitearch}/%{pkg_name}/LICENSE.txt
rm -f %{buildroot}%{python3_sitearch}/%{pkg_name}/README.txt
rm -f %{buildroot}%{python3_sitearch}/%{pkg_name}/THANKS.txt
rm -f %{buildroot}%{python3_sitearch}/%{pkg_name}/site.cfg.example

%check
cd "%{buildroot}"
%{?scl:scl enable %{scl} - << \EOF}
PYTHONPATH="%{buildroot}%{python3_sitearch}" %{__python3} -c "import numpy ; numpy.test('full', verbose=3)"
%{?scl:EOF}

%files
%doc docs-f2py LICENSE.txt README.txt THANKS.txt DEV_README.txt COMPATIBILITY site.cfg.example
%{python3_sitearch}/%{pkg_name}/__pycache__
%dir %{python3_sitearch}/%{pkg_name}
%{python3_sitearch}/%{pkg_name}/*.py*
%{python3_sitearch}/%{pkg_name}/core
%{python3_sitearch}/%{pkg_name}/doc
%{python3_sitearch}/%{pkg_name}/distutils
%{python3_sitearch}/%{pkg_name}/fft
%{python3_sitearch}/%{pkg_name}/lib
%{python3_sitearch}/%{pkg_name}/linalg
%{python3_sitearch}/%{pkg_name}/ma
%{python3_sitearch}/%{pkg_name}/numarray
%{python3_sitearch}/%{pkg_name}/oldnumeric
%{python3_sitearch}/%{pkg_name}/random
%{python3_sitearch}/%{pkg_name}/testing
%{python3_sitearch}/%{pkg_name}/tests
%{python3_sitearch}/%{pkg_name}/compat
%{python3_sitearch}/%{pkg_name}/matrixlib
%{python3_sitearch}/%{pkg_name}/polynomial
%{python3_sitearch}/%{pkg_name}-*.egg-info
%{_includedir}/numpy

%files f2py
%{_mandir}/man*/*
%{_bindir}/f2py3
%{python3_sitearch}/%{pkg_name}/f2py

%changelog
* Wed Jan 28 2015 jchaloup <jchaloup@redhat.com> - 1:1.8.2-1
- Update to 0.8.2

* Tue Mar 04 2014 Tomas Tomecek <ttomecek@redhat.com> - 1:1.7.1-10
- numpy should own %{python3_sitearch}/numpy/__pycache__ (rhbz#1072424)

* Tue Feb 11 2014 Tomas Tomecek <ttomecek@redhat.com> - 1:1.7.1-9
- Fix CVE-2014-1858, CVE-2014-1859: #1062009

* Tue Jan 14 2014 Tomas Tomecek <ttomecek@redhat.com> - 1:1.7.1-8
- update shebang to point to interpreter in collection, rhbz#1053011

* Fri Jan 10 2014 Tomas Tomecek <ttomecek@redhat.com> - 1:1.7.1-7
- keep doc directory in site-lib rhbz#1051553

* Tue Nov 19 2013 Tomas Tomecek <ttomecek@redhat.com> - 1:1.7.1-6
- RHSCL build

* Wed Sep 25 2013 Tomas Tomecek <ttomecek@redhat.com> - 1:1.7.1-5
- rebuilt with atlas 3.10, rhbz#1009069

* Wed Aug 28 2013 Tomas Tomecek <ttomecek@redhat.com> - 1:1.7.1-4
- URL Fix, rhbz#1001337

* Tue Jul 23 2013 Tomas Tomecek <ttomecek@redhat.com> - 1:1.7.1-3
- Update License
- Fix rpmlint warnings
- Increase verbosity level of tests
- Disable python 3 build
- Fix rhbz#987032 (SCL related: wrong shebang)

* Sun Jun 2 2013 Orion Poplawski <orion@nwra.com> - 1:1.7.1-2
- Specfile cleanup (bug #969854)

* Wed Apr 10 2013 Orion Poplawski <orion@nwra.com> - 1:1.7.1-1
- Update to 1.7.1

* Sat Feb 9 2013 Orion Poplawski <orion@nwra.com> - 1:1.7.0-1
- Update to 1.7.0 final

* Sun Dec 30 2012 Orion Poplawski <orion@nwra.com> - 1:1.7.0-0.5.rc1
- Update to 1.7.0rc1

* Thu Sep 20 2012 Orion Poplawski <orion@nwra.com> - 1:1.7.0-0.4.b2
- Update to 1.7.0b2
- Drop patches applied upstream

* Wed Aug 22 2012 Orion Poplawski <orion@nwra.com> - 1:1.7.0-0.3.b1
- Add patch from github pull 371 to fix python 3.3 pickle issue
- Remove cython .c source regeneration - fails now

* Wed Aug 22 2012 Orion Poplawski <orion@nwra.com> - 1:1.7.0-0.2.b1
- add workaround for rhbz#849713 (fixes FTBFS)

* Tue Aug 21 2012 Orion Poplawski <orion@cora.nwra.com> - 1:1.7.0-0.1.b1
- Update to 1.7.0b1
- Rebase python 3.3 patchs to current git master
- Drop patches applied upstream

* Sun Aug  5 2012 David Malcolm <dmalcolm@redhat.com> - 1:1.6.2-5
- rework patches for 3.3 to more directly reflect upstream's commits
- re-enable test suite on python 3
- forcibly regenerate Cython .c source to avoid import issues on Python 3.3

* Sun Aug  5 2012 Thomas Spura <tomspur@fedoraproject.org> - 1:1.6.2-4
- rebuild for https://fedoraproject.org/wiki/Features/Python_3.3
- needs unicode patch

* Fri Aug  3 2012 David Malcolm <dmalcolm@redhat.com> - 1:1.6.2-3
- remove rhel logic from with_python3 conditional

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.6.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun May 20 2012 Orion Poplawski <orion@cora.nwra.com> - 1:1.6.2-1
- Update to 1.6.2 final

* Sat May 12 2012 Orion Poplawski <orion@cora.nwra.com> - 1:1.6.2rc1-0.1
- Update to 1.6.2rc1

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.6.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Nov 7 2011 Orion Poplawski <orion@cora.nwra.com> - 1:1.6.1-1
- Update to 1.6.1

* Fri Jun 17 2011 Jon Ciesla <limb@jcomserv.net> - 1:1.6.0-2
- Bump and rebuild for BZ 712251.

* Mon May 16 2011 Orion Poplawski <orion@cora.nwra.com> - 1:1.6.0-1
- Update to 1.6.0 final

* Mon Apr 4 2011 Orion Poplawski <orion@cora.nwra.com> - 1:1.6.0-0.2.b2
- Update to 1.6.0b2
- Drop import patch fixed upstream

* Thu Mar 31 2011 Orion Poplawski <orion@cora.nwra.com> - 1:1.6.0-0.1.b1
- Update to 1.6.0b1
- Build python3  module with python3
- Add patch from upstream to fix build time import error

* Wed Mar 30 2011 Orion Poplawski <orion@cora.nwra.com> - 1:1.5.1-1
- Update to 1.5.1 final

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.5.1-0.4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Jan 13 2011 Dan Horák <dan[at]danny.cz> - 1:1.5.1-0.3
- fix the AttributeError during tests
- fix build on s390(x)

* Wed Dec 29 2010 David Malcolm <dmalcolm@redhat.com> - 1:1.5.1-0.2
- rebuild for newer python3

* Wed Oct 27 2010 Thomas Spura <tomspur@fedoraproject.org> - 1:1.5.1-0.1
- update to 1.5.1rc1
- add python3 subpackage
- some spec-cleanups

* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 1:1.4.1-6
- actually add the patch this time

* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 1:1.4.1-5
- fix segfault within %%check on 2.7 (patch 2)

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 1:1.4.1-4
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Sun Jul 18 2010 Dan Horák <dan[at]danny.cz> 1.4.1-3
- ignore the "Ticket #1299 second test" failure on s390(x)

* Thu Jun 24 2010 Jef Spaleta <jspaleta@fedoraprject.org> 1.4.1-2
- source commit fix

* Thu Jun 24 2010 Jef Spaleta <jspaleta@fedoraprject.org> 1.4.1-1
- New upstream release. Include backported doublefree patch

* Mon Apr 26 2010 Jon Ciesla <limb@jcomserv.net> 1.3.0-8
- Moved distutils back to the main package, BZ 572820.

* Thu Apr 08 2010 Jon Ciesla <limb@jcomserv.net> 1.3.0-7
- Reverted to 1.3.0 after upstream pulled 1.4.0, BZ 579065.

* Tue Mar 02 2010 Jon Ciesla <limb@jcomserv.net> 1.4.0-5
- Linking /usr/include/numpy to .h files, BZ 185079.

* Tue Feb 16 2010 Jon Ciesla <limb@jcomserv.net> 1.4.0-4
- Re-enabling atlas BR, dropping lapack Requires.

* Wed Feb 10 2010 Jon Ciesla <limb@jcomserv.net> 1.4.0-3
- Since the previous didn't work, Requiring lapack.

* Tue Feb 09 2010 Jon Ciesla <limb@jcomserv.net> 1.4.0-2
- Temporarily dropping atlas BR to work around 562577.

* Fri Jan 22 2010 Jon Ciesla <limb@jcomserv.net> 1.4.0-1
- 1.4.0.
- Dropped ARM patch, ARM support added upstream.

* Tue Nov 17 2009 Jitesh Shah <jiteshs@marvell.com> - 1.3.0-6.fa1
- Add ARM support

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jun 11 2009 Jon Ciesla <limb@jcomserv.net> 1.3.0-5
- Fixed atlas BR, BZ 505376.

* Fri Apr 17 2009 Jon Ciesla <limb@jcomserv.net> 1.3.0-4
- EVR bump for pygame chainbuild.

* Fri Apr 17 2009 Jon Ciesla <limb@jcomserv.net> 1.3.0-3
- Moved linalg, fft back to main package.

* Tue Apr 14 2009 Jon Ciesla <limb@jcomserv.net> 1.3.0-2
- Split out f2py into subpackage, thanks Peter Robinson pbrobinson@gmail.com.

* Tue Apr 07 2009 Jon Ciesla <limb@jcomserv.net> 1.3.0-1
- Update to latest upstream.
- Fixed Source0 URL.

* Thu Apr 02 2009 Jon Ciesla <limb@jcomserv.net> 1.3.0-0.rc1
- Update to latest upstream.

* Thu Mar 05 2009 Jon Ciesla <limb@jcomserv.net> 1.2.1-3
- Require python-devel, BZ 488464.

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Dec 19 2008 Jon Ciesla <limb@jcomserv.net> 1.2.1-1
- Update to 1.2.1.

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1.2.0-2
- Rebuild for Python 2.6

* Tue Oct 07 2008 Jon Ciesla <limb@jcomserv.net> 1.2.0-1
- New upstream release, added python-nose BR. BZ 465999.
- Using atlas blas, not blas-devel. BZ 461472.

* Wed Aug 06 2008 Jon Ciesla <limb@jcomserv.net> 1.1.1-1
- New upstream release

* Thu May 29 2008 Jarod Wilson <jwilson@redhat.com> 1.1.0-1
- New upstream release

* Tue May 06 2008 Jarod Wilson <jwilson@redhat.com> 1.0.4-1
- New upstream release

* Mon Feb 11 2008 Jarod Wilson <jwilson@redhat.com> 1.0.3.1-2
- Add python egg to %%files on f9+

* Wed Aug 22 2007 Jarod Wilson <jwilson@redhat.com> 1.0.3.1-1
- New upstream release

* Wed Jun 06 2007 Jarod Wilson <jwilson@redhat.com> 1.0.3-1
- New upstream release

* Mon May 14 2007 Jarod Wilson <jwilson@redhat.com> 1.0.2-2
- Drop BR: atlas-devel, since it just provides binary-compat
  blas and lapack libs. Atlas can still be optionally used
  at runtime. (Note: this is all per the atlas maintainer).

* Mon May 14 2007 Jarod Wilson <jwilson@redhat.com> 1.0.2-1
- New upstream release

* Tue Apr 17 2007 Jarod Wilson <jwilson@redhat.com> 1.0.1-4
- Update gfortran patch to recognize latest gfortran f95 support
- Resolves rhbz#236444

* Fri Feb 23 2007 Jarod Wilson <jwilson@redhat.com> 1.0.1-3
- Fix up cpuinfo bug (#229753). Upstream bug/change:
  http://projects.scipy.org/scipy/scipy/ticket/349

* Thu Jan 04 2007 Jarod Wilson <jwilson@redhat.com> 1.0.1-2
- Per discussion w/Jose Matos, Obsolete/Provide f2py, as the
  stand-alone one is no longer supported/maintained upstream

* Wed Dec 13 2006 Jarod Wilson <jwilson@redhat.com> 1.0.1-1
- New upstream release

* Tue Dec 12 2006 Jarod Wilson <jwilson@redhat.com> 1.0-2
- Rebuild for python 2.5

* Wed Oct 25 2006 Jarod Wilson <jwilson@redhat.com> 1.0-1
- New upstream release

* Wed Sep 06 2006 Jarod Wilson <jwilson@redhat.com> 0.9.8-1
- New upstream release

* Wed Apr 26 2006 Ignacio Vazquez-Abrams <ivazquez@ivazquez.net> 0.9.6-1
- Upstream update

* Thu Feb 16 2006 Ignacio Vazquez-Abrams <ivazquez@ivazquez.net> 0.9.5-1
- Upstream update

* Mon Feb 13 2006 Ignacio Vazquez-Abrams <ivazquez@ivazquez.net> 0.9.4-2
- Rebuild for Fedora Extras 5

* Thu Feb  2 2006 Ignacio Vazquez-Abrams <ivazquez@ivazquez.net> 0.9.4-1
- Initial RPM release
- Added gfortran patch from Neal Becker
