pyRT_DISORT makes atmospheric preprocessing much simpler when using the DISORT radiative
transfer code. 

Dependencies
============
- numpy
- scipy

Install
=======
Note that I've only tested this on Ubuntu. In the future I hope to automate this but for now...
- Download DISORT at: http://www.rtatmocn.com/disort/
- Install gfortran. On Ubunutu it's simple: sudo apt-get install gfortran
- Move the tarball to where you want the code and run <tar -xf disort4.0.98.tar.gz>
- cd disort4.0.98
- Run python -m numpy.f2py -c BDREF.f DISOBRDF.f DISORT.f ERRPACK.f LAPACK.f LINPAK.f RDI1MACH.f -m 
disort
- Move the newly created .so file to python's site-packages, or update PYTHONPATH. Congratulations!
You can now import disort
- Now that disort can run, install this repo using wheel

Conventions
===========
The physical units follow the following conventions:
- Altitudes are in km
- Wavelengths are in microns
- Wavenumbers are in 1/cm
- Everything else is in MKS units

If you mess with the solar spectrum, its values are at 1AU
