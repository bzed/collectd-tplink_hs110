"""
Collect power usage data from TP-Link HS110 SmartPlugs.
Requires pyHS100 version 0.2.4.2 (or a collectd build using Python3).
   pip install pyHS100==0.2.4.2

Drop tplink_hs110.py into /usr/share/collectd/python and add
the following snippet to your collectd.conf:

LoadPlugin python
<Plugin python>
        ModulePath "/usr/share/collectd/python"
        LogTraces true
        Import "tplink_hs110"
        <Module tplink_hs110>
                cr10s4 "10.11.12.13"
                coffeemachine "10.11.12.1"
        </Module>
</Plugin>


    Copyright (C) 2017 Bernd Zeimetz <bernd@bzed.de>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""

import collectd
from pyHS100 import SmartPlug
from pprint import pformat as pf

PLUGIN_NAME = 'tplink_hs110'
INTERVAL = 10 # seconds

config = {}
plugs = {}

def configure(configobj):
    global config
    global plugs
    #collectd.info('tplink_hs110: Configure with: key=%s, children=%r' % (
    #            configobj.key, configobj.children))

    config = {c.key: c.values[0] for c in configobj.children}
    collectd.info('tplink_hs110: Configured hs110 name/ip: %r' % (config))

    for name, ip in config.items():
        try:
            plug = SmartPlug(ip)
            collectd.info('tplink_hs110: %s' % pf(plug.hw_info))
        except Exception, e:
            collectd.error('tplink_hs110: Failed to connect to %s - %s' %(name, ip))
        else:
            collectd.info('tplink_hs110: Connected to %s - %s' %(name, ip))
            plugs[name] = plug


def read(data=None):
    # {u'current': 0.685227,#012 u'power': 87.350224,#012 u'total': 1.423,#012 u'voltage': 234.660149}
    global plugs

    for name, plug in plugs.items():
        plugin_instance = name
        measurements = plug.get_emeter_realtime()

        data = ['current', 'power', 'voltage', 'total']
        for i in data:
            if i == 'total':
                _type = 'power'
            else:
                _type = i
            p = collectd.Values(type=_type, type_instance=i, plugin_instance=plugin_instance)
            p.plugin = PLUGIN_NAME
            p.values = [ measurements[i]]
            p.dispatch()

collectd.register_config(configure)
collectd.register_read(read, INTERVAL)
