# SDN-RL-Routing
SDN refers to  Software Defined Network, which separates control plane
and forwarding plane.
This project aims at optimizes SDN routing algorithm based on reinforcement leaning.
Here we focus on normal metrics in network:
+ delay
+ loss
+ throughput
Also，we 
# Install Mininet
refer to http://mininet.org/download/
```shell
git clone https://github.com/mininet/mininet

mininet/util/install.sh -a
```

# Install Ryu Controller
```shell
pip install ryu
```
# Run DRL SDN Routing Algorithm 
Controller connects to mininet with OpenFlow Protocol, here we choose OpenFlow version 1.3.
Common OpenFlow Protocol Version: v1.0, v1.1, v1.2, v1.3


# Initialize Mininet
```shell
python3 testbed.py
```

# Initialize Controller

# Initialize DRL Agent



