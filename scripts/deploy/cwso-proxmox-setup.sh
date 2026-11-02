#!/bin/bash
# CWSO Proxmox LXC Automated Setup Script
# Provisions an LXC container on Proxmox VE with CWSO deployed
# Usage: bash cwso-proxmox-setup.sh [OPTIONS]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration (defaults)
CTID=201
HOSTNAME="cwso-prod-01"
IP_ADDRESS="192.168.1.100/24"
GATEWAY="192.168.1.1"
CORES=2
MEMORY=4096
SWAP=2048
STORAGE="local"
BRIDGE="vmbr0"
TEMPLATE="/var/lib/vz/template/cache/ubuntu-20.04-standard_20.04-1_amd64.tar.zst"
NON_INTERACTIVE=0
AUTO_MODE=0
# The JWT secret comes from the CWSO_JWT_SECRET environment variable only
# (T694): there is no secret file default.
SECRET_ENV_VAR="CWSO_JWT_SECRET"

# Pinned downloads (SEC-T694-11, T726, looked up 2026-11-02). Each download goes
# to a mktemp -d directory in the container and is checked with sha256sum
# before use; a mismatch stops the setup. To update a pin, take the new
# version and checksum from the official source named on each line.
# Docker convenience script, pinned to a docker/docker-install commit
# (https://github.com/docker/docker-install/commit/af185b580a79972aefcb30700ff83893adf3964e),
# sha256 of install.sh at that commit:
DOCKER_INSTALL_URL="https://raw.githubusercontent.com/docker/docker-install/af185b580a79972aefcb30700ff83893adf3964e/install.sh"
DOCKER_INSTALL_SHA256="2b102d809152ea157a59f171319f489d971273b2d26dd7e9a6d1d737ce89289d"
# Docker Engine version passed to the script's --version option
# (https://github.com/moby/moby/releases/tag/docker-v29.9.2):
DOCKER_VERSION="29.9.2"
# Standalone docker-compose binary
# (https://github.com/docker/compose/releases/tag/v5.6.1, checksums.txt):
COMPOSE_VERSION="v5.6.1"
COMPOSE_SHA256_X86_64="47737f4236e6d3ccea7291995203f8f018058783b4c3a9469119811a0b5db8c0"
COMPOSE_SHA256_AARCH64="42cfa75f51ad0ccf290bad37899e0038a8c10a0069e85233ecc1d53e3ff1347d"

# Functions
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

require_jwt_secret() {
    if [ -z "${CWSO_JWT_SECRET:-}" ]; then
        print_error "${SECRET_ENV_VAR} is not set"
        echo "Export ${SECRET_ENV_VAR} before running the setup, for example from your secret store." >&2
        exit 1
    fi
}

# Print the .env line for CWSO_JWT_SECRET (SEC-T694-08). docker-compose
# reads a single-quoted .env value literally ($, #, spaces and " keep their
# meaning as plain characters); a quote is escaped as \'. A backslash has no
# unambiguous form there, so such a value is refused. Errors name the
# variable only, never the value.
compose_env_line() {
    local value
    value="$(printf '%s' "$CWSO_JWT_SECRET" | tr -d '\r\n')"
    if [[ "$value" == *\\* ]]; then
        print_error "${SECRET_ENV_VAR} contains a backslash, which a docker-compose .env value cannot hold literally" >&2
        exit 1
    fi
    printf "%s='%s'\n" "$SECRET_ENV_VAR" "${value//\'/\\\'}"
}

show_usage() {
    cat << 'EOF'
CWSO Proxmox LXC Setup Script

Usage: CWSO_JWT_SECRET=... bash cwso-proxmox-setup.sh [OPTIONS]

Environment:
  CWSO_JWT_SECRET          Required. Written as CWSO_JWT_SECRET='<value>' (single-
                           quoted, so docker-compose reads it literally) to
                           /opt/cwso/repo/.env in the container, mode 600 and
                           owner root; docker-compose reads it there for the
                           jwt_secret secret. The value stays at rest in that
                           file. A value with a backslash is refused.

Options:
  --ctid <ID>              Container ID (default: 201)
  --hostname <name>        Container hostname (default: cwso-prod-01)
  --ip <addr/mask>         Container IP with netmask (default: 192.168.1.100/24)
  --gateway <ip>           Gateway IP (default: 192.168.1.1)
  --cores <n>              CPU cores (default: 2)
  --memory <MB>            Memory in MB (default: 4096)
  --swap <MB>              Swap in MB (default: 2048)
  --storage <pool>         Storage pool name (default: local)
  --bridge <name>          Network bridge (default: vmbr0)
  --template <path>        LXC template path
  --auto                   Use all defaults and auto-answer prompts
  --non-interactive        Require no user interaction
  --help                   Show this help message

Examples:
  bash cwso-proxmox-setup.sh
  bash cwso-proxmox-setup.sh --auto
  bash cwso-proxmox-setup.sh --ctid 202 --hostname cwso-staging-01
  bash cwso-proxmox-setup.sh --ip 10.0.0.50/24 --gateway 10.0.0.1

EOF
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --ctid)
                CTID="$2"
                shift 2
                ;;
            --hostname)
                HOSTNAME="$2"
                shift 2
                ;;
            --ip)
                IP_ADDRESS="$2"
                shift 2
                ;;
            --gateway)
                GATEWAY="$2"
                shift 2
                ;;
            --cores)
                CORES="$2"
                shift 2
                ;;
            --memory)
                MEMORY="$2"
                shift 2
                ;;
            --swap)
                SWAP="$2"
                shift 2
                ;;
            --storage)
                STORAGE="$2"
                shift 2
                ;;
            --bridge)
                BRIDGE="$2"
                shift 2
                ;;
            --template)
                TEMPLATE="$2"
                shift 2
                ;;
            --auto)
                AUTO_MODE=1
                NON_INTERACTIVE=1
                shift
                ;;
            --non-interactive)
                NON_INTERACTIVE=1
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

verify_proxmox() {
    print_header "Verifying Proxmox Environment"

    # Check if running on Proxmox
    if [ ! -f /etc/proxmox-release ]; then
        print_error "This script must be run on a Proxmox VE host"
        exit 1
    fi

    print_success "Proxmox VE detected"

    # Check LXC tools
    if ! command -v pct &> /dev/null; then
        print_error "pct command not found. Install Proxmox VE LXC tools."
        exit 1
    fi

    print_success "pct tool available"

    # Check template
    if [ ! -f "$TEMPLATE" ]; then
        print_warning "Template not found: $TEMPLATE"
        print_info "Available templates:"
        ls -lh /var/lib/vz/template/cache/ 2>/dev/null || echo "  (none found)"

        if [ $NON_INTERACTIVE -eq 1 ]; then
            exit 1
        fi

        read -p "Enter template path or press Enter to use default: " TEMPLATE_INPUT
        if [ -n "$TEMPLATE_INPUT" ]; then
            TEMPLATE="$TEMPLATE_INPUT"
            if [ ! -f "$TEMPLATE" ]; then
                print_error "Template not found: $TEMPLATE"
                exit 1
            fi
        fi
    fi

    print_success "Template found: $TEMPLATE"

    # Check if container ID already exists
    if pct status $CTID &>/dev/null; then
        print_warning "Container $CTID already exists"
        if [ $NON_INTERACTIVE -eq 1 ]; then
            print_error "Cannot proceed with existing container in non-interactive mode"
            exit 1
        fi
        read -p "Destroy existing container? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pct stop $CTID 2>/dev/null || true
            pct destroy $CTID
            print_success "Container $CTID destroyed"
        else
            print_error "Cannot proceed with existing container"
            exit 1
        fi
    fi

    # Check storage pool
    if ! pvesm list $STORAGE &>/dev/null; then
        print_error "Storage pool not found: $STORAGE"
        print_info "Available storage:"
        pvesm list
        exit 1
    fi

    print_success "Storage pool available: $STORAGE"

    # Check network bridge
    if ! ip link show $BRIDGE &>/dev/null; then
        print_warning "Network bridge not found: $BRIDGE"
        print_info "Available bridges:"
        ip link show | grep "^ *[0-9]*:" | grep -i bridge
        exit 1
    fi

    print_success "Network bridge available: $BRIDGE"
}

confirm_configuration() {
    print_header "Container Configuration"

    echo "Configuration:"
    echo "  Container ID:    $CTID"
    echo "  Hostname:        $HOSTNAME"
    echo "  IP Address:      $IP_ADDRESS"
    echo "  Gateway:         $GATEWAY"
    echo "  CPU Cores:       $CORES"
    echo "  Memory:          ${MEMORY}MB"
    echo "  Swap:            ${SWAP}MB"
    echo "  Storage:         $STORAGE"
    echo "  Network Bridge:  $BRIDGE"
    echo "  Template:        $TEMPLATE"
    echo ""

    if [ $NON_INTERACTIVE -eq 0 ]; then
        read -p "Proceed with container creation? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Cancelled by user"
            exit 0
        fi
    fi

    print_success "Configuration confirmed"
}

create_container() {
    print_header "Creating LXC Container"

    print_info "Creating container $CTID with CWSO configuration..."

    pct create $CTID "$TEMPLATE" \
        --hostname "$HOSTNAME" \
        --cores "$CORES" \
        --memory "$MEMORY" \
        --swap "$SWAP" \
        --storage "$STORAGE" \
        --net0 "name=eth0,bridge=$BRIDGE,ip=$IP_ADDRESS,gw=$GATEWAY" \
        --onboot 1 \
        --start 1

    print_success "Container created"
}

wait_container_boot() {
    print_header "Waiting for Container to Boot"

    print_info "Waiting for container $CTID to be ready..."

    for i in {1..30}; do
        if pct exec $CTID test -f /etc/os-release 2>/dev/null; then
            print_success "Container is ready"
            return 0
        fi
        echo -ne "\r  Attempt $i/30... "
        sleep 2
    done

    print_error "Container failed to boot after 60 seconds"
    exit 1
}

configure_container_network() {
    print_header "Configuring Container Network"

    print_info "Setting up network configuration..."

    # Configure network inside container
    pct exec $CTID tee /etc/network/interfaces > /dev/null << EOF
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
    address $(echo $IP_ADDRESS | cut -d/ -f1)
    netmask $(ipcalc -m $IP_ADDRESS | cut -d= -f2)
    gateway $GATEWAY
    dns-nameservers 8.8.8.8 8.8.4.4
EOF

    # Restart networking
    pct exec $CTID systemctl restart networking

    # Verify connectivity
    sleep 2
    if pct exec $CTID ping -c 1 8.8.8.8 &>/dev/null; then
        print_success "Network configured and verified"
    else
        print_warning "Network configuration may need manual adjustment"
    fi
}

install_docker() {
    print_header "Installing Docker"

    print_info "Updating system packages..."
    pct exec $CTID apt-get update
    pct exec $CTID apt-get upgrade -y

    print_info "Installing Docker ${DOCKER_VERSION} (pinned, checksum verified)..."
    # $1 URL, $2 sha256, $3 Docker version; mktemp -d instead of a fixed /tmp path.
    pct exec $CTID -- sh -c 'set -eu
        dir="$(mktemp -d)"
        trap "rm -rf \"$dir\"" EXIT
        curl -fsSL "$1" -o "$dir/install.sh"
        printf "%s  %s\n" "$2" "$dir/install.sh" | sha256sum -c -
        sh "$dir/install.sh" --version "$3"' sh \
        "$DOCKER_INSTALL_URL" "$DOCKER_INSTALL_SHA256" "$DOCKER_VERSION"

    print_info "Enabling Docker service..."
    pct exec $CTID systemctl enable docker
    pct exec $CTID systemctl start docker

    # Verify Docker
    if pct exec $CTID docker --version &>/dev/null; then
        print_success "Docker installed"
    else
        print_error "Docker installation failed"
        exit 1
    fi
}

install_docker_compose() {
    print_header "Installing Docker Compose"

    local arch sha
    arch="$(pct exec $CTID -- uname -m)"
    case "$arch" in
        x86_64) sha="$COMPOSE_SHA256_X86_64" ;;
        aarch64) sha="$COMPOSE_SHA256_AARCH64" ;;
        *)
            print_error "No pinned docker-compose checksum for this architecture"
            exit 1
            ;;
    esac

    print_info "Installing docker-compose ${COMPOSE_VERSION} (pinned, checksum verified)..."
    # $1 URL, $2 sha256; verified in a mktemp -d directory, then installed.
    pct exec $CTID -- sh -c 'set -eu
        dir="$(mktemp -d)"
        trap "rm -rf \"$dir\"" EXIT
        curl -fsSL "$1" -o "$dir/docker-compose"
        printf "%s  %s\n" "$2" "$dir/docker-compose" | sha256sum -c -
        install -m 0755 "$dir/docker-compose" /usr/local/bin/docker-compose' sh \
        "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-${arch}" \
        "$sha"

    if pct exec $CTID docker-compose --version &>/dev/null; then
        print_success "docker-compose installed"
    else
        print_error "docker-compose installation failed"
        exit 1
    fi
}

deploy_cwso() {
    print_header "Deploying CWSO"

    print_info "Creating CWSO deployment directory..."
    pct exec $CTID mkdir -p /opt/cwso/data

    print_info "Cloning CWSO repository..."
    pct exec $CTID git clone https://gitlab.com/em-age/emage.code.git /opt/cwso/repo

    print_info "Setting up CWSO configuration..."
    pct exec $CTID bash << 'EOF'
cd /opt/cwso/repo

# Copy docker-compose
cp deploy/docker-compose-t226.yml docker-compose.yml

# Copy environment
cp deploy/t226-phase2.env .env

chmod 600 .env

# Add Parquet store configuration
echo "PARQUET_STORE_PATH=/opt/cwso/data" >> .env
EOF

    # Configure JWT: docker-compose reads CWSO_JWT_SECRET from the project .env
    # (mode 600, owner root) for the jwt_secret secret of docker-compose.yml.
    # The value is passed over stdin, never on argv, and never printed (T694).
    # It stays at rest in that file (SEC-T694-08).
    print_info "Writing ${SECRET_ENV_VAR} to /opt/cwso/repo/.env for the jwt_secret secret..."
    # Built first, so a refused value stops the setup (set -e) before any write.
    local env_line
    env_line="$(compose_env_line)"
    printf '%s\n' "$env_line" | pct exec $CTID -- sh -c \
        'umask 077 && cat >> /opt/cwso/repo/.env && chmod 600 /opt/cwso/repo/.env'

    print_info "Starting CWSO services..."
    pct exec $CTID bash << 'EOF'
cd /opt/cwso/repo
docker-compose pull
docker-compose up -d
EOF

    print_success "CWSO deployed"
}

verify_deployment() {
    print_header "Verifying Deployment"

    print_info "Waiting for services to be ready..."
    sleep 10

    # Check container running
    if pct status $CTID | grep -q "running"; then
        print_success "Container is running"
    else
        print_error "Container is not running"
        exit 1
    fi

    # Check services
    print_info "Checking CWSO services..."
    pct exec $CTID bash << 'EOF'
cd /opt/cwso/repo

# Check if docker-compose services are running
if docker-compose ps | grep -q "Up"; then
    echo "✓ Services running"
else
    echo "✗ Services not running"
    docker-compose logs --tail=50 orchestrator git-shadow merge-engine rollout sia-executor
    exit 1
fi

# Test health endpoint
if curl -s http://localhost:8080/health | grep -q "status"; then
    echo "✓ Orchestrator health check passed"
else
    echo "⚠ Health check response unclear"
fi
EOF

    print_success "Deployment verified"
}

show_summary() {
    print_header "Deployment Complete"

    echo "✓ Container $CTID created and running"
    echo ""
    echo "Container Details:"
    echo "  ID:       $CTID"
    echo "  Hostname: $HOSTNAME"
    echo "  IP:       $(echo $IP_ADDRESS | cut -d/ -f1)"
    echo "  Location: /opt/cwso/repo"
    echo ""
    echo "Access Container:"
    echo "  pct enter $CTID"
    echo ""
    echo "View Logs:"
    echo "  pct exec $CTID docker-compose logs -f --tail=50"
    echo ""
    echo "Check Services:"
    echo "  pct exec $CTID docker-compose ps"
    echo ""
    echo "Test Health:"
    echo "  pct exec $CTID curl http://localhost:8080/health"
    echo ""
    echo "SSH (if SSH configured):"
    echo "  ssh root@$(echo $IP_ADDRESS | cut -d/ -f1)"
    echo ""
}

# Main execution
main() {
    print_header "CWSO Proxmox LXC Setup"

    parse_arguments "$@"
    require_jwt_secret
    verify_proxmox
    confirm_configuration
    create_container
    wait_container_boot
    configure_container_network
    install_docker
    install_docker_compose
    deploy_cwso
    verify_deployment
    show_summary

    print_success "CWSO is ready on Proxmox!"
    print_info "Run 'pct enter $CTID' to access the container"
}

# Execute main
main "$@"
