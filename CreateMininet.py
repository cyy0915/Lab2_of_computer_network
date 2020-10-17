from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time

from sys import argv

filename = '1Mtest'

class SingleSwitchTopo( Topo ):
    def build(self, n):
        switch = self.addSwitch('s1')
        hostName = ['h'+str(i) for i in range(0,n)]
        host = [self.addHost(h) for h in hostName]
        for h in host:
            self.addLink(h, switch, bw=5)

setLogLevel('info')

#P2P
for hostNum in range(2, 11):
    t = open('timelog', 'a')
    t.write('\n'+str(hostNum)+':')
    t.close()
    topo = SingleSwitchTopo(hostNum)
    net = Mininet( topo=topo,
                    host=CPULimitedHost, link=TCLink,
                    autoStaticArp=True )
    net.start()
    for i in range(hostNum):
        hostName = 'h'+str(i)
        host = net.getNodeByName(hostName)
        host.cmd('rm -rf '+hostName)
        host.cmd('mkdir '+hostName)
        host.cmd('cd '+hostName)
        if i==0:
            host.cmd('cp ../'+filename+' ./'+filename)
            host.cmd('python3 ../P2P_server.py &')
            time.sleep(0.5)
        else:
            host.cmd('python3 ../P2P_client.py &')
        host.cmd('cd ..')
    time.sleep(20)
    net.stop()
#C/S
for hostNum in range(2, 11):
    t = open('timelog', 'a')
    t.write('\n'+str(hostNum)+':')
    t.close()
    topo = SingleSwitchTopo(hostNum)
    net = Mininet( topo=topo,
                    host=CPULimitedHost, link=TCLink,
                    autoStaticArp=True )
    net.start()
    for i in range(hostNum):
        hostName = 'h'+str(i)
        host = net.getNodeByName(hostName)
        host.cmd('rm -rf '+hostName)
        host.cmd('mkdir '+hostName)
        host.cmd('cd '+hostName)
        if i==0:
            host.cmd('cp ../'+filename+' ./'+filename)
            host.cmd('python3 ../CS_server.py &')
            time.sleep(0.5)
        else:
            host.cmd('python3 ../CS_client.py &')
        host.cmd('cd ..')
    time.sleep(20)
    net.stop()