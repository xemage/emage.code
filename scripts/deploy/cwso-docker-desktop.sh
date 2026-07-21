#!/bin/bash
# CWSO Docker Desktop Automated Setup Script
# Quick deployment for local development and testing
# Usage: bash cwso-docker-desktop.sh [--update] [--clean] [--help]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="${REPO_ROOT:-.}"
DEPLOY_DIR="${REPO_ROOT}/deploy/local-dev"
DOCKER_COMPOSE_SOURCE="${REPO_ROOT}/deploy/docker-compose-t226.yml"
ENV_SOURCE="${REPO_ROOT}/deploy/t226-phase2.env"
JWT_SOURCE="${REPO_ROOT}/deploy/.env.jwt.dev"

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

check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        echo "Download from: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    print_success "Docker is installed: $(docker --version)"

    # Check Docker daemon
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        echo "Please start Docker Desktop and try again"
        exit 1
    fi
    print_success "Docker daemon is running"

    # Check docker-compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed"
        exit 1
    fi
    print_success "docker-compose is installed: $(docker-compose --version)"

    # Check available ports
    local occupied_ports=()
    for port in 8080 8787 8788 8789; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            occupied_ports+=($port)
        fi
    done

    if [ ${#occupied_ports[@]} -gt 0 ]; then
        print_warning "Ports in use: ${occupied_ports[@]}"
        echo "These ports are already in use. You may need to:"
        echo "  - Stop existing CWSO: cd $DEPLOY_DIR && docker-compose down"
        echo "  - Or use different ports (edit docker-compose.yml)"
    fi

    print_success "Prerequisites check complete"
}

setup_deploy_directory() {
    print_header "Setting Up Deployment Directory"

    # Create deploy directory
    if [ ! -d "$DEPLOY_DIR" ]; then
        mkdir -p "$DEPLOY_DIR"
        print_success "Created deployment directory: $DEPLOY_DIR"
    else
        print_success "Deployment directory exists: $DEPLOY_DIR"
    fi
}

copy_configuration() {
    print_header "Configuring CWSO"

    # Check source files exist
    if [ ! -f "$DOCKER_COMPOSE_SOURCE" ]; then
        print_error "docker-compose file not found: $DOCKER_COMPOSE_SOURCE"
        exit 1
    fi

    if [ ! -f "$ENV_SOURCE" ]; then
        print_error "Environment file not found: $ENV_SOURCE"
        exit 1
    fi

    # Copy docker-compose
    cp "$DOCKER_COMPOSE_SOURCE" "$DEPLOY_DIR/docker-compose.yml"
    print_success "Copied docker-compose configuration"

    # Copy environment template
    cp "$ENV_SOURCE" "$DEPLOY_DIR/.env"
    print_success "Copied environment configuration"

    # Configure JWT
    if [ -f "$JWT_SOURCE" ]; then
        JWT_SECRET=$(tr -d '\r\n' < "$JWT_SOURCE")
        echo "JWT_SECRET=$JWT_SECRET" >> "$DEPLOY_DIR/.env"
        print_success "Configured JWT secret from development source"
    else
        print_warning "Development JWT not found at $JWT_SOURCE"
        echo "Generating new JWT secret..."
        JWT_SECRET=$(head -c 32 /dev/urandom | base64)
        echo "JWT_SECRET=$JWT_SECRET" >> "$DEPLOY_DIR/.env"
        print_success "Generated new JWT secret"
    fi
}

pull_images() {
    print_header "Pulling Docker Images"

    cd "$DEPLOY_DIR"

    if docker-compose pull; then
        print_success "All images pulled successfully"
    else
        print_warning "Some images may not be available, will build locally"
    fi
}

start_services() {
    print_header "Starting CWSO Services"

    cd "$DEPLOY_DIR"

    if docker-compose up -d; then
        print_success "Services started"
    else
        print_error "Failed to start services"
        exit 1
    fi

    # Wait for services to be ready
    echo "Waiting for services to be ready..."
    sleep 5
}

verify_deployment() {
    print_header "Verifying Deployment"

    cd "$DEPLOY_DIR"

    # Check container status
    if ! docker-compose ps | grep -q "Up"; then
        print_error "Services are not running"
        docker-compose logs
        exit 1
    fi

    local all_running=true
    for service in orchestrator rollout-proxy; do
        if docker-compose ps | grep "$service" | grep -q "Up"; then
            print_success "$service is running"
        else
            print_error "$service is not running"
            all_running=false
        fi
    done

    if [ "$all_running" = false ]; then
        print_error "Some services failed to start"
        print_header "Service Logs"
        docker-compose logs
        exit 1
    fi

    # Test health endpoints
    echo "Testing health endpoints..."
    sleep 2

    if curl -s http://localhost:8080/health | grep -q "healthy" 2>/dev/null || curl -s http://localhost:8080/health | grep -q "status" 2>/dev/null; then
        print_success "Orchestrator health check passed"
    else
        print_warning "Orchestrator health check didn't respond as expected"
        echo "Response: $(curl -s http://localhost:8080/health)"
    fi

    if curl -s http://localhost:8787/health | grep -q "healthy" 2>/dev/null || curl -s http://localhost:8787/health | grep -q "status" 2>/dev/null; then
        print_success "Rollout proxy health check passed"
    else
        print_warning "Rollout proxy health check didn't respond as expected"
        echo "Response: $(curl -s http://localhost:8787/health)"
    fi
}

show_status() {
    print_header "CWSO Deployment Status"

    cd "$DEPLOY_DIR"

    echo "Container Status:"
    docker-compose ps

    echo ""
    echo "Configuration Location: $DEPLOY_DIR"
    echo "Environment File: $DEPLOY_DIR/.env"
    echo "Docker Compose File: $DEPLOY_DIR/docker-compose.yml"

    echo ""
    echo "Available Endpoints:"
    echo "  Orchestrator:   http://localhost:8080"
    echo "  Rollout Proxy:  http://localhost:8787"
    echo "  Git Shadow:     http://localhost:8788"
    echo "  Merge Engine:   http://localhost:8789"
}

show_usage() {
    print_header "CWSO Docker Desktop Setup"

    cat << 'EOF'
Usage: bash cwso-docker-desktop.sh [OPTION]

Options:
  (no args)     Full setup: check prereqs, configure, pull images, start services
  --update      Update images and restart services (preserves data)
  --clean       Stop and remove all containers (⚠️ deletes volumes)
  --status      Show current deployment status
  --logs        Follow service logs
  --help        Show this help message

Examples:
  bash cwso-docker-desktop.sh              # Full setup
  bash cwso-docker-desktop.sh --update     # Update to latest images
  bash cwso-docker-desktop.sh --status     # Check status
  bash cwso-docker-desktop.sh --logs       # Watch logs

After successful deployment, test with:
  curl http://localhost:8080/health

To stop services:
  cd deploy/local-dev && docker-compose down

To view logs:
  cd deploy/local-dev && docker-compose logs -f

EOF
}

update_deployment() {
    print_header "Updating CWSO Deployment"

    cd "$DEPLOY_DIR"

    echo "Pulling latest images..."
    docker-compose pull

    echo "Recreating containers..."
    docker-compose up -d --force-recreate

    sleep 5
    verify_deployment

    print_success "Deployment updated successfully"
}

clean_deployment() {
    print_header "Cleaning CWSO Deployment"

    cd "$DEPLOY_DIR"

    print_warning "This will stop and remove all containers and volumes"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_success "Cleanup cancelled"
        return
    fi

    echo "Stopping services..."
    docker-compose down -v

    print_success "Deployment cleaned"
    print_warning "All data has been removed. Run setup again to restart."
}

show_logs() {
    print_header "CWSO Service Logs"

    cd "$DEPLOY_DIR"

    echo "Press Ctrl+C to stop"
    sleep 2

    docker-compose logs -f
}

# Main execution
main() {
    local command="${1:-setup}"

    case "$command" in
        --help|-h)
            show_usage
            ;;
        --status|-s)
            show_status
            ;;
        --update|-u)
            update_deployment
            ;;
        --clean|-c)
            clean_deployment
            ;;
        --logs|-l)
            show_logs
            ;;
        "")
            # Full setup
            check_prerequisites
            setup_deploy_directory
            copy_configuration
            pull_images
            start_services
            verify_deployment
            show_status

            print_success "CWSO is ready!"
            echo ""
            echo "Next steps:"
            echo "  1. Test health: curl http://localhost:8080/health"
            echo "  2. View logs: cd $DEPLOY_DIR && docker-compose logs"
            echo "  3. Run tests: pytest tests/"
            ;;
        *)
            print_error "Unknown option: $command"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Execute main
main "$@"
