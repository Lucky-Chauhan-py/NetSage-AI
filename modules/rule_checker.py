"""
rule_checker.py – Rule-based pre-diagnosis for NetSage AI.

Analyses raw Cisco show output text and symptom descriptions using
regex/keyword pattern matching to flag common network faults before
sending to the AI engine.

Each rule returns a FindingDict if triggered, or None.
The run_all_rules() function is the primary public interface.
"""

from __future__ import annotations

import re
from typing import TypedDict


# ---------------------------------------------------------------------------
# Type definition for a rule finding
# ---------------------------------------------------------------------------

class FindingDict(TypedDict):
    rule_name: str
    issue: str
    severity: str
    recommendation: str
    matched_evidence: str


# ---------------------------------------------------------------------------
# Individual rule functions
# ---------------------------------------------------------------------------

def _check_interface_shutdown(text: str) -> FindingDict | None:
    """Detect administratively shutdown interfaces."""
    pattern = re.compile(
        r"([\w/]+)\s+\S+\s+YES\s+\S+\s+administratively down\s+down",
        re.IGNORECASE,
    )
    match = pattern.search(text)
    if match:
        iface = match.group(1)
        return FindingDict(
            rule_name="INTERFACE_SHUTDOWN",
            issue=f"Interface '{iface}' is administratively shut down",
            severity="High",
            recommendation=f"Run: interface {iface} → no shutdown",
            matched_evidence=match.group(0).strip(),
        )
    # Also check 'shutdown' in interface config block
    if re.search(r"^\s*shutdown\s*$", text, re.MULTILINE | re.IGNORECASE):
        return FindingDict(
            rule_name="INTERFACE_SHUTDOWN",
            issue="A 'shutdown' command is present in an interface configuration",
            severity="High",
            recommendation="Issue 'no shutdown' on the affected interface",
            matched_evidence="shutdown (found in interface config)",
        )
    return None


def _check_duplicate_ip(text: str) -> FindingDict | None:
    """Detect duplicate IP address conflicts."""
    patterns = [
        r"duplicate\s+(?:ip\s+)?address",
        r"ip\s+address\s+conflict",
        r"address\s+already\s+in\s+use",
        r"%IP-4-DUPADDR",
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return FindingDict(
                rule_name="DUPLICATE_IP",
                issue="Duplicate IP address conflict detected",
                severity="Medium",
                recommendation="Assign unique IP addresses to each host. Use DHCP to prevent conflicts.",
                matched_evidence=match.group(0).strip(),
            )
    return None


def _check_wrong_subnet_mask(text: str) -> FindingDict | None:
    """
    Detect common subnet mask mismatches.
    Looks for /16 or /8 masks in typical /24 environments.
    """
    # Find all subnet masks in show output
    mask_pattern = re.compile(r"255\.\d+\.\d+\.\d+")
    masks = mask_pattern.findall(text)
    suspicious = [m for m in masks if m in ("255.0.0.0", "255.255.0.0")]
    if suspicious:
        return FindingDict(
            rule_name="WRONG_SUBNET_MASK",
            issue=f"Potentially wrong subnet mask(s) detected: {set(suspicious)}",
            severity="Medium",
            recommendation="Verify subnet masks match the intended network design (typically /24 = 255.255.255.0)",
            matched_evidence=", ".join(set(suspicious)),
        )
    return None


def _check_gateway_mismatch(symptom: str, text: str) -> FindingDict | None:
    """Detect gateway mismatch based on symptom keywords."""
    keywords = [
        "wrong gateway", "incorrect gateway", "gateway mismatch",
        "wrong default gateway", "default gateway incorrect",
    ]
    combined = (symptom + " " + text).lower()
    for kw in keywords:
        if kw in combined:
            return FindingDict(
                rule_name="GATEWAY_MISMATCH",
                issue="Default gateway mismatch detected",
                severity="Medium",
                recommendation="Verify the default gateway on the host matches the router interface IP on the same subnet",
                matched_evidence=f"Keyword match: '{kw}'",
            )
    return None


def _check_missing_default_route(text: str) -> FindingDict | None:
    """Detect missing default route in routing table."""
    has_route_table = bool(
        re.search(r"show\s+ip\s+route|Codes:|Gateway of last resort", text, re.IGNORECASE)
    )
    if not has_route_table:
        return None
    has_default = bool(
        re.search(
            r"Gateway of last resort is (?!not set)|\bS\*\b|0\.0\.0\.0/0|ip route 0\.0\.0\.0",
            text,
            re.IGNORECASE,
        )
    )
    no_default_explicitly = bool(
        re.search(r"Gateway of last resort is not set", text, re.IGNORECASE)
    )
    if no_default_explicitly or (has_route_table and not has_default):
        return FindingDict(
            rule_name="MISSING_DEFAULT_ROUTE",
            issue="No default route configured – internet-bound traffic will be dropped",
            severity="High",
            recommendation="Add: ip route 0.0.0.0 0.0.0.0 <next-hop-ip>",
            matched_evidence="'Gateway of last resort is not set' or no S* route found",
        )
    return None


def _check_missing_vlan(text: str) -> FindingDict | None:
    """Detect references to VLANs that do not appear in VLAN database."""
    # Look for access vlan assignments that might not be in the VLAN DB
    access_vlans = re.findall(r"switchport access vlan (\d+)", text, re.IGNORECASE)
    vlan_db = re.findall(r"^(\d+)\s+\S+\s+(active|act/unsup)", text, re.MULTILINE | re.IGNORECASE)
    vlan_db_ids = {v[0] for v in vlan_db}
    if access_vlans and vlan_db_ids:
        missing = [v for v in access_vlans if v not in vlan_db_ids]
        if missing:
            return FindingDict(
                rule_name="MISSING_VLAN",
                issue=f"VLAN(s) {missing} assigned to ports but not found in VLAN database",
                severity="High",
                recommendation=f"Create the missing VLAN(s): vlan {missing[0]}; name <NAME>",
                matched_evidence=f"Access VLAN {missing[0]} not in 'show vlan brief'",
            )
    return None


def _check_trunk_misconfiguration(text: str) -> FindingDict | None:
    """Detect trunk vs access port misconfigurations."""
    # Access port configured as trunk
    if re.search(r"switchport mode trunk", text, re.IGNORECASE) and re.search(
        r"switchport mode access", text, re.IGNORECASE
    ):
        return FindingDict(
            rule_name="TRUNK_ACCESS_CONFLICT",
            issue="Port has both trunk and access mode configuration – conflict detected",
            severity="High",
            recommendation="Remove conflicting mode. Use 'switchport mode trunk' OR 'switchport mode access' – not both",
            matched_evidence="Both 'switchport mode trunk' and 'switchport mode access' present",
        )
    # Show interfaces trunk returns empty (no trunk ports)
    if re.search(r"show interfaces trunk", text, re.IGNORECASE) and not re.search(
        r"trunking", text, re.IGNORECASE
    ):
        return FindingDict(
            rule_name="MISSING_TRUNK",
            issue="No trunk ports found – expected trunk link may be configured as access",
            severity="High",
            recommendation="Configure trunk: switchport mode trunk on the uplink interface",
            matched_evidence="'show interfaces trunk' returned no trunking ports",
        )
    return None


def _check_vlan_not_allowed_on_trunk(text: str) -> FindingDict | None:
    """Detect VLANs missing from trunk allowed VLAN list."""
    # Look for pattern like: Fa0/x  1-19, 21-4094 (gap = vlan 20 missing)
    allowed_pattern = re.search(
        r"Vlans allowed on trunk\s*\n\S+\s+([\d,\-]+)", text, re.IGNORECASE
    )
    if not allowed_pattern:
        return None
    allowed_str = allowed_pattern.group(1)
    # If the allowed list doesn't contain 'all' or '1-4094', flag it
    if "1-4094" not in allowed_str and "all" not in allowed_str.lower():
        return FindingDict(
            rule_name="VLAN_NOT_ALLOWED_ON_TRUNK",
            issue=f"Trunk does not allow all VLANs – allowed list: {allowed_str}",
            severity="Medium",
            recommendation="Add missing VLANs: switchport trunk allowed vlan add <vlan-id>",
            matched_evidence=f"Trunk allowed VLANs: {allowed_str}",
        )
    return None


def _check_dhcp_disabled(text: str) -> FindingDict | None:
    """Detect DHCP service issues."""
    if re.search(r"no\s+service\s+dhcp", text, re.IGNORECASE):
        return FindingDict(
            rule_name="DHCP_DISABLED",
            issue="DHCP service is disabled on the router",
            severity="High",
            recommendation="Enable DHCP service: service dhcp",
            matched_evidence="'no service dhcp' found in running config",
        )
    if re.search(r"no\s+ip\s+dhcp\s+pool", text, re.IGNORECASE):
        return FindingDict(
            rule_name="DHCP_POOL_MISSING",
            issue="No DHCP pool configured",
            severity="High",
            recommendation="Configure DHCP pool: ip dhcp pool LAN; network <subnet> <mask>; default-router <gateway>",
            matched_evidence="'no ip dhcp pool' – no pool definition found",
        )
    return None


def _check_dns_disabled(text: str, symptom: str) -> FindingDict | None:
    """Detect DNS configuration issues."""
    combined = (symptom + " " + text).lower()
    dns_issue_keywords = ["dns", "cannot resolve", "unknown host", "name resolution"]
    has_dns_complaint = any(kw in combined for kw in dns_issue_keywords)
    if not has_dns_complaint:
        return None
    if re.search(r"dns\s*:\s*0\.0\.0\.0|dns.server.*0\.0\.0\.0", text, re.IGNORECASE):
        return FindingDict(
            rule_name="DNS_NOT_CONFIGURED",
            issue="DNS server configured as 0.0.0.0 – DNS resolution will fail",
            severity="Medium",
            recommendation="Set DNS server in DHCP pool: dns-server 8.8.8.8 or configure ip name-server",
            matched_evidence="DNS: 0.0.0.0 found in IP configuration",
        )
    if re.search(r"no\s+ip\s+name.server", text, re.IGNORECASE):
        return FindingDict(
            rule_name="DNS_NOT_CONFIGURED",
            issue="No DNS name server configured on router",
            severity="Medium",
            recommendation="Add: ip name-server 8.8.8.8 on the router",
            matched_evidence="'no ip name-server' found",
        )
    return None


def _check_missing_nat_interface(text: str) -> FindingDict | None:
    """Detect missing NAT inside/outside interface configuration."""
    has_nat_config = bool(
        re.search(r"ip nat (inside|outside) source", text, re.IGNORECASE)
    )
    if not has_nat_config:
        return None
    has_inside = bool(re.search(r"ip nat inside", text, re.IGNORECASE))
    has_outside = bool(re.search(r"ip nat outside", text, re.IGNORECASE))
    if not has_inside:
        return FindingDict(
            rule_name="NAT_INSIDE_MISSING",
            issue="NAT inside not configured on any interface",
            severity="High",
            recommendation="Add 'ip nat inside' to the internal interface",
            matched_evidence="NAT config present but no 'ip nat inside' on interface",
        )
    if not has_outside:
        return FindingDict(
            rule_name="NAT_OUTSIDE_MISSING",
            issue="NAT outside not configured on any interface",
            severity="High",
            recommendation="Add 'ip nat outside' to the external/WAN interface",
            matched_evidence="NAT config present but no 'ip nat outside' on interface",
        )
    return None


def _check_ospf_area_mismatch(text: str) -> FindingDict | None:
    """Detect OSPF area mismatches between routers."""
    areas = re.findall(r"network\s+[\d\.]+\s+[\d\.]+\s+area\s+(\d+)", text, re.IGNORECASE)
    unique_areas = set(areas)
    if len(unique_areas) > 1:
        return FindingDict(
            rule_name="OSPF_AREA_MISMATCH",
            issue=f"Multiple OSPF area IDs detected: {unique_areas} – routers may not form adjacency",
            severity="High",
            recommendation="Ensure all routers on the same segment use the same OSPF area number",
            matched_evidence=f"OSPF areas found: {unique_areas}",
        )
    # OSPF neighbor stuck in INIT/EXSTART
    if re.search(r"INIT|EXSTART|EXCHANGE", text, re.IGNORECASE) and re.search(
        r"show ip ospf neighbor", text, re.IGNORECASE
    ):
        return FindingDict(
            rule_name="OSPF_STUCK_STATE",
            issue="OSPF neighbor stuck in non-FULL state (INIT/EXSTART/EXCHANGE)",
            severity="High",
            recommendation="Check: same area, same hello/dead timers, no ACL blocking OSPF (224.0.0.5), MTU match",
            matched_evidence="OSPF neighbor in non-FULL state",
        )
    return None


def _check_port_security_violation(text: str) -> FindingDict | None:
    """Detect port security shutdown."""
    if re.search(r"Port Status\s*:\s*Secure-shutdown", text, re.IGNORECASE):
        return FindingDict(
            rule_name="PORT_SECURITY_VIOLATION",
            issue="Port security violation has shut down the switch port",
            severity="High",
            recommendation="Recover: interface <port>; shutdown; no shutdown. Or: errdisable recovery",
            matched_evidence="Port Status: Secure-shutdown (from show port-security interface)",
        )
    return None


def _check_wrong_vlan_assignment(text: str, symptom: str) -> FindingDict | None:
    """Detect when hosts are assigned to wrong VLAN based on symptom."""
    combined = (symptom + " " + text).lower()
    if any(kw in combined for kw in ["wrong vlan", "incorrect vlan", "vlan mismatch", "wrong broadcast domain"]):
        return FindingDict(
            rule_name="WRONG_VLAN_ASSIGNMENT",
            issue="Port may be assigned to an incorrect VLAN",
            severity="Medium",
            recommendation="Verify: show run interface <port>; correct with: switchport access vlan <correct-vlan>",
            matched_evidence="Keyword match: wrong/incorrect VLAN in symptom",
        )
    return None


# ---------------------------------------------------------------------------
# Main rule runner
# ---------------------------------------------------------------------------

def run_all_rules(symptom: str, show_output: str) -> list[FindingDict]:
    """
    Run all rule checks against the provided symptom and show output.

    Returns a list of FindingDict entries, one per triggered rule.
    Results are deduplicated by rule_name.
    """
    combined_text = (symptom or "") + "\n" + (show_output or "")
    findings: list[FindingDict] = []
    seen_rules: set[str] = set()

    def _add(finding: FindingDict | None) -> None:
        if finding and finding["rule_name"] not in seen_rules:
            findings.append(finding)
            seen_rules.add(finding["rule_name"])

    _add(_check_interface_shutdown(combined_text))
    _add(_check_duplicate_ip(combined_text))
    _add(_check_wrong_subnet_mask(combined_text))
    _add(_check_gateway_mismatch(symptom, show_output))
    _add(_check_missing_default_route(combined_text))
    _add(_check_missing_vlan(combined_text))
    _add(_check_trunk_misconfiguration(combined_text))
    _add(_check_vlan_not_allowed_on_trunk(combined_text))
    _add(_check_dhcp_disabled(combined_text))
    _add(_check_dns_disabled(combined_text, symptom))
    _add(_check_missing_nat_interface(combined_text))
    _add(_check_ospf_area_mismatch(combined_text))
    _add(_check_port_security_violation(combined_text))
    _add(_check_wrong_vlan_assignment(combined_text, symptom))

    return findings


def get_rule_summary(findings: list[FindingDict]) -> dict[str, int]:
    """Return a summary dict of severity counts from a findings list."""
    summary = {"High": 0, "Medium": 0, "Low": 0, "Critical": 0}
    for f in findings:
        sev = f.get("severity", "Low")
        summary[sev] = summary.get(sev, 0) + 1
    return summary
