import argparse
import json
import logging

from functools import partial
import socket

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch, Controller
from mininet.topo import Topo

from utils import load_topo


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


# net: Topo
def gen_request(net, data):
    host_src = net.hosts[data["src"]]
    host_dst = net.hosts[data["dst"]]


if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='testbed_run.log', level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--topo", default='Abilene', type=str,
                        help="available topology: test | Abilene| GEANT")
    parser.add_argument("--testbed-ip", default="127.0.0.1", type=str, help="ip address of testbed")
    parser.add_argument("--testbed-port", default=5000, type=int, help="port  of testbed")
    # mininet default ip: 127.0.0.1 default port: 6653 这里可以不用指定，mininet的默认设置
    # ryu控制器参数
    # --ofp-tcp-listen-port 6653 tcp监听端口
    # --ofp-ssl-listen-port 6653 ssl监听端口
    parser.add_argument("--controller-ip", default="127.0.0.1", type=str, help="controller ip address")
    parser.add_argument("--controller-port", default=6653, type=int, help="controller port")

    args = parser.parse_args()
    topo_name = args.topo

    node_num, link_set, bandwidth, loss = load_topo(topo_name)
    net_topo = CustomTopo(node_num, link_set, bandwidth, loss)
    net = Mininet(topo=net_topo, switch=partial(OVSSwitch, protocols='OpenFlow13'),
                  link=TCLink, controller=None)
    net.addController('ryu-controller', controller=RemoteController, ip=args.controller_ip, port=args.controller_port)
    net.start()
    CLI(net)

    # bind socket
    # 接收DRL根据流量矩阵产生的流量
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((args.testbed_ip, args.testbed_port))
    s.listen(1)

    conn, addr = s.accept()
    logger.info('Accepted connection from %s ', addr)

    while True:
        msg = conn.recv(1024)
        logger.info(msg)


