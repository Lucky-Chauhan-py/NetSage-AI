# Few-Shot Examples for NetSage AI Diagnosis

These examples demonstrate the expected input/output format for the AI diagnosis engine.

---

## Example 1: Interface Shutdown

**Input:**
```
Symptom: PC cannot ping the default gateway 192.168.1.1
Topology: PC0 connected to Switch1 Fa0/1, Switch1 connects to Router0 Gi0/0
Show Output:
Router0# show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.1.1     YES manual administratively down down
GigabitEthernet0/1    203.0.113.1     YES manual up                    up
```

**Expected Output:**
```json
{
  "root_cause": "The router interface GigabitEthernet0/0 is administratively shutdown, preventing any Layer 3 communication from the PC subnet. The interface status shows 'administratively down' which means someone explicitly issued a shutdown command.",
  "confidence": "97",
  "osi_layer": "Layer 1 – Physical",
  "evidence": "show ip interface brief reveals: GigabitEthernet0/0 192.168.1.1 - Status: administratively down, Protocol: down. This directly explains why PC cannot reach 192.168.1.1.",
  "next_command": "show running-config interface GigabitEthernet0/0",
  "fix_steps": "Step 1: Enter interface configuration mode: Router0(config)# interface GigabitEthernet0/0\nStep 2: Bring up the interface: Router0(config-if)# no shutdown\nStep 3: Verify: Router0# show ip interface brief\nStep 4: Test connectivity from PC: ping 192.168.1.1"
}
```

---

## Example 2: Missing Static Route

**Input:**
```
Symptom: PC0 (192.168.1.10) can ping Router0 (192.168.1.1) but cannot reach server at 10.10.10.5
Topology: Router0 Gi0/0 connects to PC network 192.168.1.0/24, Router0 Gi0/1 connects to Router1, Router1 Gi0/0 connects to server network 10.10.10.0/24
Show Output:
Router0# show ip route
Codes: C - connected, S - static, I - IGRP
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
C    172.16.0.0/30 is directly connected, GigabitEthernet0/1
Router0# show ip interface brief
GigabitEthernet0/0    192.168.1.1    YES manual up    up
GigabitEthernet0/1    172.16.0.1     YES manual up    up
```

**Expected Output:**
```json
{
  "root_cause": "Router0 has no route to the destination network 10.10.10.0/24 where the server resides. The routing table shows only directly connected networks and no static or dynamic route pointing to the server subnet via Router1.",
  "confidence": "94",
  "osi_layer": "Layer 3 – Network",
  "evidence": "show ip route on Router0 shows only: C 192.168.1.0/24 and C 172.16.0.0/30. There is no route entry for 10.10.10.0/24. Router1's network (172.16.0.2) should be the next hop.",
  "next_command": "show ip route on Router1 to verify it has the return route",
  "fix_steps": "Step 1: Add static route on Router0: Router0(config)# ip route 10.10.10.0 255.255.255.0 172.16.0.2\nStep 2: Add return route on Router1: Router1(config)# ip route 192.168.1.0 255.255.255.0 172.16.0.1\nStep 3: Verify routing table: Router0# show ip route\nStep 4: Test end-to-end: PC0> ping 10.10.10.5"
}
```

---

## Example 3: VLAN Trunking Misconfiguration

**Input:**
```
Symptom: VLAN 20 hosts can communicate within the same switch but cannot reach VLAN 20 hosts on Switch2
Topology: Switch1 and Switch2 connected via Fa0/24. Hosts on VLAN 10 and VLAN 20 on both switches.
Show Output:
Switch1# show interfaces trunk
Port        Mode         Encapsulation  Status        Native vlan
Fa0/24      on           802.1q         trunking      1
Port        Vlans allowed on trunk
Fa0/24      1-19, 21-4094
Switch1# show vlan brief
VLAN Name      Status    Ports
1    default   active    Fa0/24
10   Sales      active    Fa0/1, Fa0/2
20   HR         active    Fa0/3, Fa0/4
```

**Expected Output:**
```json
{
  "root_cause": "VLAN 20 is explicitly excluded from the trunk link between Switch1 and Switch2. The trunk on Fa0/24 allows VLANs 1-19 and 21-4094, meaning VLAN 20 was specifically removed from the allowed VLANs list.",
  "confidence": "99",
  "osi_layer": "Layer 2 – Data Link",
  "evidence": "show interfaces trunk reveals: Fa0/24 Vlans allowed on trunk = '1-19, 21-4094'. VLAN 20 is conspicuously absent from this range, confirming it was removed with a switchport trunk allowed vlan remove 20 command.",
  "next_command": "show interfaces Fa0/24 trunk",
  "fix_steps": "Step 1: Add VLAN 20 back to the trunk: Switch1(config)# interface FastEthernet0/24\nStep 2: Switch1(config-if)# switchport trunk allowed vlan add 20\nStep 3: Repeat on Switch2 if needed\nStep 4: Verify: Switch1# show interfaces trunk\nStep 5: Test: Ping between VLAN 20 hosts across switches"
}
```
