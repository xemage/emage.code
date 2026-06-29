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

show_usage() {
    cat << 'EOF'
CWSO Proxmox LXC Setup Script

Usage: bash cwso-proxmox-setup.sh [OPTIONS]

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

    print_info "Installing Docker..."
    pct exec $CTID curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    pct exec $CTID bash /tmp/get-docker.sh

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

    print_info "Installing docker-compose..."
    pct exec $CTID curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    pct exec $CTID chmod +x /usr/local/bin/docker-compose

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

# Configure JWT (use development JWT for testing)
if [ -f deploy/.env.jwt.dev ]; then
    JWT_SECRET=$(tr -d '\r\n' < deploy/.env.jwt.dev)
    echo "JWT_SECRET=$JWT_SECRET" >> .env
fi

# Add Parquet store configuration
echo "PARQUET_STORE_PATH=/opt/cwso/data" >> .env
EOF

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
    docker-compose logs
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
    echo "  pct exec $CTID docker-compose logs -f"
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
