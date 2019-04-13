"""
Collect power usage data from TP-Link HS110 SmartPlugs.

    Copyright (C) 2017 Bernd Zeimetz <bernd@bzed.de

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
import re
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
    # {u'total_wh': 4474, u'current_ma': 9099, u'power_mw': 2245448, u'voltage_mv': 249459}

    global plugs

    for name, plug in plugs.items():
        plugin_instance = name
        measurements = plug.get_emeter_realtime()

        data = measurements.keys()
        for i in data:
            type_instance = re.sub('_.*', '', i)
            if 'total' == type_instance:
                _type = 'power'
            else:
                _type = type_instance
            p = collectd.Values(type=_type, type_instance=type_instance, plugin_instance=plugin_instance)
            p.plugin = PLUGIN_NAME
            measurement = measurements[i]
            if '_m' in i:
                # measurement is in milli volt/watt/ampere
                measurement = measurement / 1000.0
            p.values = [ measurement ]
            p.dispatch()

collectd.register_config(configure)
collectd.register_read(read, INTERVAL)
