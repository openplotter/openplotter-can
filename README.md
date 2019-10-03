## openplotter-can

OpenPlotter app to manage CAN BUS adapters. 

### Installing

#### For production

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **production** and just install this app from *OpenPlotter Apps* tab.

#### For development

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **development**.

Install openplotter-can dependencies:

`sudo apt install canboat`

Clone openplotter-can:

`git clone https://github.com/openplotter/openplotter-can`

Make your changes and test them installing the app:

`cd openplotter-can`
`sudo python3 setup.py install`

Pull request your changes to github and we will check and add them to the next version of the [Debian package](https://launchpad.net/~openplotter/+archive/ubuntu/openplotter/).

### Documentation

https://openplotter.readthedocs.io

### Support

http://forum.openmarine.net/forumdisplay.php?fid=1
