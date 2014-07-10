#!/bin/sh
echo "be sure to install first"
echo "apt-get install python-avahi python-dbus"
# Then either use system packges with 
#python virtualenv.py --system-site-packages xwot

# or another workaround is to just manually copy the dbus files/libraries directly to your virtualenv:
python virtualenv.py xwot
cp -r /usr/lib/python2.7/dist-packages/avahi/ xwot/lib/python2.7/site-packages/
cp -r /usr/lib/python2.7/dist-packages/dbus/ xwot/lib/python2.7/site-packages/
cp -r /usr/lib/python2.7/dist-packages/_dbus_* xwot/lib/python2.7/site-packages/

# Finally install the required packages
xwot/bin/pip install -r requirements.txt
