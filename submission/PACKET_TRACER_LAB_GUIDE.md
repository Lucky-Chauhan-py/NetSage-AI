# Cisco Packet Tracer (.pkt) Lab Topology & Configuration Guide
### Project: NetSage AI – AI-Assisted Cisco Packet Tracer Troubleshooting Platform
**Submission File Name:** `Lucky Chauhan-KCC Institute Of Technology And Management-NetSage AI.pkt`

---

## 1. Network Topology Architecture

```
                                  [ ISP / Internet Cloud ]
                                             |
                                    (Serial0/0/1 - WAN)
                                             |
                                      +--------------+
                                      | Router0 (HQ) | [Cisco 2911 ISR]
                                      +--------------+
                                       /            \
                       (Gig0/0 Trunk) /              \ (Serial0/0/0 WAN Link: 10.0.0.0/30)
                                     /                \
                       +---------------+            +------------------+
                       | Switch1 (Core)|            | Router1 (Branch) | [Cisco 2911 ISR]
                       +---------------+            +------------------+
                        /      |      \                       |
          (Fa0/1 Trunk)/ (Fa0/2)       \(Fa0/3)               | (Gig0/0: 192.168.30.0/24)
                      /        |        \                     |
           +------------+   +--------+   +----------+   +-------------------+
           | Switch2    |   |Server0 |   | PC2      |   | PC3 (Branch User) |
           | (Access)   |   | (DHCP/ |   | (VLAN 20)|   | (192.168.30.50)   |
           +------------+   |  DNS)  |   |192.168.  |   +-------------------+
            /          \    +--------+   |  20.50   |
     (Fa0/1)            \(Fa0/2)         +----------+
    +---------+      +---------+
    | PC0     |      | PC1     |
    | (VLAN 10|      | (VLAN 20|
    | Sales)  |      | Eng)    |
    +---------+      +---------+
```

---

## 2. Complete Device Addressing Table

| Device | Interface | IP Address | Subnet Mask | Default Gateway | Purpose |
|---|---|---|---|---|---|
| **Router0 (HQ)** | Gig0/0.10 | 192.168.10.1 | 255.255.255.0 | N/A | VLAN 10 Gateway (RoAS) |
| **Router0 (HQ)** | Gig0/0.20 | 192.168.20.1 | 255.255.255.0 | N/A | VLAN 20 Gateway (RoAS) |
| **Router0 (HQ)** | Serial0/0/0 | 10.0.0.1 | 255.255.255.252 | N/A | WAN Serial to Branch (DCE) |
| **Router0 (HQ)** | Gig0/1 | 203.0.113.1 | 255.255.255.248 | N/A | WAN / NAT Public Interface |
| **Router1 (Branch)** | Serial0/0/0 | 10.0.0.2 | 255.255.255.252 | N/A | WAN Serial to HQ (DTE) |
| **Router1 (Branch)** | Gig0/0 | 192.168.30.1 | 255.255.255.0 | N/A | Branch LAN Gateway |
| **Server0** | FastEthernet0 | 192.168.10.254 | 255.255.255.0 | 192.168.10.1 | DHCP Relay / DNS / HTTP Server |
| **PC0 (Sales)** | FastEthernet0 | DHCP (192.168.10.x)| 255.255.255.0 | 192.168.10.1 | VLAN 10 Endpoint |
| **PC1 (Eng)** | FastEthernet0 | DHCP (192.168.20.x)| 255.255.255.0 | 192.168.20.1 | VLAN 20 Endpoint |
| **PC2 (Eng)** | FastEthernet0 | 192.168.20.50 | 255.255.255.0 | 192.168.20.1 | VLAN 20 Static Host |
| **PC3 (Branch)**| FastEthernet0 | 192.168.30.50 | 255.255.255.0 | 192.168.30.1 | Branch Office Host |

---

## 3. Cisco IOS Configuration Commands (Copy-Paste Ready)

### 🔹 Router0 (HQ Router - Cisco 2911)
Open CLI on Router0 and paste:
```cisco
enable
configure terminal
hostname Router0-HQ

! Enable Routing
ip routing

! Configure Router-on-a-Stick Subinterfaces
interface GigabitEthernet0/0
 no ip address
 no shutdown
 exit

interface GigabitEthernet0/0.10
 description Gateway for VLAN 10 (Sales)
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
 ip helper-address 192.168.10.254
 ip nat inside
 exit

interface GigabitEthernet0/0.20
 description Gateway for VLAN 20 (Engineering)
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
 ip helper-address 192.168.10.254
 ip nat inside
 exit

! WAN Serial Interface to Branch
interface Serial0/0/0
 description WAN Link to Branch Router1
 ip address 10.0.0.1 255.255.255.252
 clock rate 64000
 no shutdown
 exit

! Internet / Simulated ISP Interface
interface GigabitEthernet0/1
 description Simulated Internet Interface
 ip address 203.0.113.1 255.255.255.248
 ip nat outside
 no shutdown
 exit

! Dynamic Routing (OSPF Area 0)
router ospf 1
 router-id 1.1.1.1
 network 192.168.10.0 0.0.0.255 area 0
 network 192.168.20.0 0.0.0.255 area 0
 network 10.0.0.0 0.0.0.3 area 0
 default-information originate
 exit

! Default Static Route to Internet
ip route 0.0.0.0 0.0.0.0 203.0.113.2

! NAT Overload (PAT)
access-list 1 permit 192.168.0.0 0.0.255.255
ip nat inside source list 1 interface GigabitEthernet0/1 overload

! Security & Management
banner motd # Authorized Access Only - NetSage AI Monitoring Active #
line vty 0 4
 password cisco
 login
 exit
end
write memory
```

---

### 🔹 Router1 (Branch Router - Cisco 2911)
Open CLI on Router1 and paste:
```cisco
enable
configure terminal
hostname Router1-Branch

! Enable Routing
ip routing

! WAN Serial to HQ
interface Serial0/0/0
 description WAN Link to HQ Router0
 ip address 10.0.0.2 255.255.255.252
 no shutdown
 exit

! Branch LAN Interface
interface GigabitEthernet0/0
 description Branch LAN Gateway
 ip address 192.168.30.1 255.255.255.0
 no shutdown
 exit

! OSPF Area 0
router ospf 1
 router-id 2.2.2.2
 network 192.168.30.0 0.0.0.255 area 0
 network 10.0.0.0 0.0.0.3 area 0
 exit

! Security & Banner
banner motd # Router1 Branch Office - NetSage AI #
line vty 0 4
 password cisco
 login
 exit
end
write memory
```

---

### 🔹 Switch1 (Core Switch - Cisco 2960)
Open CLI on Switch1 and paste:
```cisco
enable
configure terminal
hostname Switch1-Core

! Create VLANs in Database
vlan 10
 name Sales
 exit
vlan 20
 name Engineering
 exit
vlan 30
 name Management
 exit

! 802.1Q Trunk uplink to Router0
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown
 exit

! 802.1Q Trunk downlink to Switch2
interface FastEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown
 exit

! Access Ports
interface FastEthernet0/2
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown
 exit

interface FastEthernet0/3
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 no shutdown
 exit
end
write memory
```

---

### 🔹 Switch2 (Access Switch - Cisco 2960)
Open CLI on Switch2 and paste:
```cisco
enable
configure terminal
hostname Switch2-Access

! Create VLANs
vlan 10
 name Sales
 exit
vlan 20
 name Engineering
 exit

! Trunk to Switch1
interface FastEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 no shutdown
 exit

! Access Port for PC0 with Port Security
interface FastEthernet0/2
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 spanning-tree portfast
 no shutdown
 exit

! Access Port for PC1
interface FastEthernet0/3
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 no shutdown
 exit
end
write memory
```

---

## 4. How to Save & Submit Your Packet Tracer (.pkt) File

1. Open **Cisco Packet Tracer**.
2. Connect the devices according to the topology diagram.
3. Paste the CLI commands above for **Router0**, **Router1**, **Switch1**, and **Switch2**.
4. Configure **Server0** with IP `192.168.10.254`, subnet mask `255.255.255.0`, gateway `192.168.10.1`, and turn ON DHCP service.
5. Verify ping connectivity from `PC0` to `Router1` (`ping 192.168.30.1`).
6. Click **File → Save As...**
7. Save the file with the **exact mandatory name**:
   ```
   Lucky Chauhan-KCC Institute Of Technology And Management-NetSage AI.pkt
   ```
