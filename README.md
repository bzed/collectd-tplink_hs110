# collectd-tplink_hs110
Collect power usage data from TP-Link HS110 SmartPlugs.


Requires pyHS100 version 0.2.4.2 (or a collectd build using Python3).
   pip install pyHS100==0.2.4.2

Drop tplink_hs110.py into /usr/share/collectd/python and add
the following snippet to your collectd.conf - add one line with
name + IP for each device you want to monitor:

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
