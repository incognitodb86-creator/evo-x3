#!/usr/bin/env bash
set -euo pipefail

# EVO-X3 U18 Egress Firewall for Playwright MCP Podman Network (Plan P1-3)
# Creates an isolated Podman bridge network `evo-mcp-egress` and inserts nftables/firewalld
# egress drop rules blocking RFC1918, Tailscale CGNAT (100.64.0.0/10), link-local,
# loopback, and host local addresses so Playwright can reach ONLY public internet.

NET_NAME="evo-mcp-egress"
SUBNET_CIDR="10.89.44.0/24"
BRIDGE_IF="evo-mcp0"

if ! podman network exists "$NET_NAME"; then
  podman network create \
    --driver bridge \
    --interface-name "$BRIDGE_IF" \
    --subnet "$SUBNET_CIDR" \
    "$NET_NAME"
fi

echo "Applying nftables egress blocks on bridge interface $BRIDGE_IF ($SUBNET_CIDR)..."

# Create dedicated nftables table for evo-mcp egress isolation (idempotent even when table does not exist yet)
nft add table inet evo_mcp_egress 2>/dev/null || true
nft flush table inet evo_mcp_egress 2>/dev/null || true
nft -f - <<EOF
table inet evo_mcp_egress {
    chain forward {
        type filter hook forward priority filter - 10; policy accept;
        iifname "${BRIDGE_IF}" ip daddr {
            10.0.0.0/8,
            172.16.0.0/12,
            192.168.0.0/16,
            100.64.0.0/10,
            169.254.0.0/16,
            127.0.0.0/8
        } counter reject with icmp type admin-prohibited
        iifname "${BRIDGE_IF}" ip6 daddr {
            fc00::/7,
            fe80::/10,
            ::1/128
        } counter reject with icmpv6 type admin-prohibited
    }
    chain input {
        type filter hook input priority filter - 10; policy accept;
        iifname "${BRIDGE_IF}" ip daddr 10.89.44.1 udp dport 53 accept
        iifname "${BRIDGE_IF}" ip daddr 10.89.44.1 tcp dport 53 accept
        iifname "${BRIDGE_IF}" meta l4proto tcp counter reject with tcp reset
        iifname "${BRIDGE_IF}" counter drop
    }
}
EOF

echo "Done. Verify U18 pass test (5) from inside the Playwright container:"
echo "  - Connections to 127.0.0.1:8080/8081, LAN gateway, QNAP, and tailnet nodes MUST fail."
echo "  - Public HTTPS page load MUST succeed."
