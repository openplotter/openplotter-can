## openplotter-can

OpenPlotter app to manage CAN BUS adapters. 

### Installing

#### For production

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **production** and just install this app from *OpenPlotter Apps* tab.

#### For development

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **development**.

Install openplotter-can dependencies:

`sudo apt install canboat python3-pyudev can-utils python3-serial`

Clone the repository:

`git clone https://github.com/openplotter/openplotter-can`

Make your changes and create the package:

```
cd openplotter-can
dpkg-buildpackage -b
```

Install the package:

```
cd ..
sudo dpkg -i openplotter-can_x.x.x-xxx_all.deb
```

Run post-installation script:

`sudo canPostInstall`

Run:

`openplotter-can`

Make your changes and repeat package, installation and post-installation steps to test. Pull request your changes to github and we will check and add them to the next version of the [Debian package](https://launchpad.net/~openplotter/+archive/ubuntu/openplotter).

### Documentation

https://openplotter.readthedocs.io

### Support

http://forum.openmarine.net/forumdisplay.php?fid=1