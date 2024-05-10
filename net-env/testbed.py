import argparse
from functools import partial

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.topo import Topo


def load_topo(topo_name):
    topo_file = open("../topology/%s/%s-Topo.txt" % (topo_name, topo_name))
    topo_info = topo_file.readlines()
    node_num, link_num = map(int, topo_info[0].split())
    link_set = []
    bandwidth = []
    loss = []
    for i in range(link_num):
        node1, node2, link_wight, link_capacity, link_loss = map(int, topo_info[i + 1].split())
        link_set.append([node1 - 1, node2 - 1])
        bandwidth.append(float(link_capacity) / 1000)
        loss.append(link_loss)
    return node_num, link_set, bandwidth, loss


class CustomTopo(Topo):
    def __init__(self, node_num, link_set, bandwidth, loss, **params):
        self._node_num = node_num
        self._link_set = link_set
        self._bandwidth = bandwidth
        self._loss = loss
        self._switches = []
        self._hosts = []
        super().__init__(**params)

    def build(self):
        # add switch: s0, s1, s2...
        for i in range(self._node_num):
            switch = self.addSwitch("s" + str(i + 1))
            self._switches.append(switch)

        # add link between switches
        for i in range(len(self._link_set)):
            id1 = self._link_set[i][0]
            id2 = self._link_set[i][1]
            self.addLink(self._switches[id1], self._switches[id2],
                         bw=self._bandwidth[i], delay='5ms', loss=self._loss[i], max_queue_size=1000)

        # add hosts connected to switch
        # mac address : 00:00:00:00:00:01 - 00:00:00:00:00:ff
        # ip address (private address):10.0.0.1 - 10.255.255.255
        for i in range(self._node_num):
            host = self.addHost("h" + str(i + 1), mac="00:00:00:00:00:%02x" % (i + 1), ip="10.0.0.%d" % (i + 1))
            self._hosts.append(host)
            self.addLink(self._switches[i], self._hosts[i], bw=1000, delay='0ms')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--topo", default='Abilene', type=str,
                        help="available topology: test | Abilene| GEANT")
    parser.add_argument("--testbed-ip", default="127.0.0.1", type=str, help="ip address of testbed")
    parser.add_argument("--testbed-port", default=5000, type=int, help="port  of testbed")
    parser.add_argument("--controller-ip", default="127.0.0.1", type=str, help="controller ip address")
    parser.add_argument("--controller-port", default=5001, type=int, help="controller port")

    args = parser.parse_args()
    topo_name = args.topo
    node_num, link_set, bandwidth, loss = load_topo(topo_name)
    net_topo = CustomTopo(node_num, link_set, bandwidth, loss)
    net = Mininet(topo=net_topo, switch=partial(OVSSwitch, protocols='OpenFlow13'),
                  link=TCLink, controller=None)
    net.addController('controller', controller=RemoteController, ip=args.controller_ip, port=args.controller_port)
    net.start()
    CLI(net)