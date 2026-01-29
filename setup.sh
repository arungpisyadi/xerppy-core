#!/bin/bash

# Project Setup Script
# This script sets up and runs the xerppy-core project
# Supports: Linux, macOS, WSL/Git Bash on Windows

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
PYTHON_VERSION_FILE="$BACKEND_DIR/.python-version"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# ============================================================================
# Utility Functions
# ============================================================================

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if grep -q Microsoft /proc/version 2>/dev/null; then
            echo "WSL"
        else
            echo "Linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macOS"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        echo "GitBash"
    else
        echo "Unknown"
    fi
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ============================================================================
# Python Setup Functions
# ============================================================================

get_required_python_version() {
    if [[ -f "$PYTHON_VERSION_FILE" ]]; then
        cat "$PYTHON_VERSION_FILE" | tr -d '[:space:]'
    else
        print_warning "Python version file not found at $PYTHON_VERSION_FILE"
        echo "3.11"
    fi
}

check_python_version() {
    local required_version="$1"
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed"
        return 1
    fi
    
    local installed_version
    installed_version=$(python3 --version 2>&1 | sed 's/Python //' | sed 's/\([0-9]\+\.[0-9]\+\).*/\1/')
    
    if [[ "$installed_version" == "$required_version" ]]; then
        print_success "Python $installed_version is installed (required: $required_version)"
        return 0
    else
        print_warning "Python $installed_version is installed but $required_version is required"
        return 1
    fi
}

install_python() {
    local version="$1"
    local os=$(detect_os)
    
    print_step "Installing Python $version on $os..."
    
    case "$os" in
        "Linux"|"WSL")
            if command_exists apt-get; then
                sudo apt-get update
                sudo apt-get install -y python${version} python${version}-venv python3-pip
            elif command_exists yum; then
                sudo yum install -y python${version}
            elif command_exists dnf; then
                sudo dnf install -y python${version}
            else
                print_error "Unsupported package manager. Please install Python $version manually."
                return 1
            fi
            ;;
        "macOS")
            if command_exists brew; then
                brew install python@${version}
            else
                print_info "Homebrew not found. Please install Python $version from https://python.org"
                return 1
            fi
            ;;
        "GitBash")
            print_info "On Windows, please install Python $version from https://python.org"
            print_info "Or use Windows Subsystem for Linux (WSL)"
            return 1
            ;;
        *)
            print_error "Unsupported operating system: $os"
            return 1
            ;;
    esac
    
    print_success "Python $version installation initiated"
}

# ============================================================================
# Node.js Setup Functions
# ============================================================================

check_node_version() {
    if ! command_exists node; then
        print_error "Node.js is not installed"
        return 1
    fi
    
    local installed_version
    installed_version=$(node --version 2>&1 | sed 's/v//')
    print_success "Node.js $installed_version is installed"
    return 0
}

install_node() {
    local os=$(detect_os)
    
    print_step "Installing Node.js on $os..."
    
    case "$os" in
        "Linux"|"WSL")
            if command_exists apt-get; then
                curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
                sudo apt-get install -y nodejs
            elif command_exists yum; then
                curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
                sudo yum install -y nodejs
            elif command_exists dnf; then
                curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
                sudo dnf install -y nodejs
            else
                print_error "Unsupported package manager. Please install Node.js manually."
                return 1
            fi
            ;;
        "macOS")
            if command_exists brew; then
                brew install node
            else
                print_info "Homebrew not found. Please install Node.js from https://nodejs.org"
                return 1
            fi
            ;;
        "GitBash")
            print_info "Please install Node.js from https://nodejs.org"
            return 1
            ;;
        *)
            print_error "Unsupported operating system: $os"
            return 1
            ;;
    esac
    
    print_success "Node.js installation initiated"
}

# ============================================================================
# Backend Setup Functions
# ============================================================================

setup_backend() {
    print_step "Setting up backend..."
    
    if [[ ! -d "$BACKEND_DIR" ]]; then
        print_error "Backend directory not found at $BACKEND_DIR"
        return 1
    fi
    
    cd "$BACKEND_DIR"
    
    # Check and install Python if needed
    local required_python_version
    required_python_version=$(get_required_python_version)
    
    if ! check_python_version "$required_python_version"; then
        if ! install_python "$required_python_version"; then
            print_error "Failed to install Python $required_python_version"
            return 1
        fi
    fi
    
    # Check if uv is installed
    if ! command_exists uv; then
        print_step "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
    
    # Install dependencies
    print_step "Installing backend dependencies with uv sync..."
    if ! uv sync; then
        print_error "Failed to install backend dependencies"
        return 1
    fi
    print_success "Backend dependencies installed"
    
    # Create admin user
    print_step "Creating admin user..."
    uv run python -m app.scripts.create_admin interactive
    
    print_success "Backend setup complete"
}

start_backend() {
    print_step "Starting backend development server..."
    cd "$BACKEND_DIR"
    uv run python main.py
}

# ============================================================================
# Frontend Setup Functions
# ============================================================================

setup_frontend() {
    print_step "Setting up frontend..."
    
    if [[ ! -d "$FRONTEND_DIR" ]]; then
        print_error "Frontend directory not found at $FRONTEND_DIR"
        return 1
    fi
    
    cd "$FRONTEND_DIR"
    
    # Check and install Node.js if needed
    if ! check_node_version; then
        if ! install_node; then
            print_error "Failed to install Node.js"
            return 1
        fi
    fi
    
    # Install dependencies
    print_step "Installing frontend dependencies with npm..."
    if ! npm install; then
        print_error "Failed to install frontend dependencies"
        return 1
    fi
    print_success "Frontend dependencies installed"
    
    print_success "Frontend setup complete"
}

start_frontend() {
    print_step "Starting frontend development server..."
    cd "$FRONTEND_DIR"
    npm run dev
}

# ============================================================================
# Main Setup Function
# ============================================================================

setup_all() {
    local os=$(detect_os)
    
    echo -e "${BOLD}========================================${NC}"
    echo -e "${BOLD}  xerppy-core Project Setup${NC}"
    echo -e "${BOLD}========================================${NC}"
    echo ""
    print_info "Detected OS: $os"
    echo ""
    
    # Setup backend
    if ! setup_backend; then
        print_error "Backend setup failed"
        exit 1
    fi
    
    echo ""
    
    # Setup frontend
    if ! setup_frontend; then
        print_error "Frontend setup failed"
        exit 1
    fi
    
    echo ""
    print_success "All setup complete!"
    echo ""
    echo -e "${BOLD}To start the development servers:${NC}"
    echo "  1. In one terminal: ./setup.sh start-backend"
    echo "  2. In another terminal: ./setup.sh start-frontend"
    echo ""
    echo -e "${BOLD}Or start both in background:${NC}"
    echo "  ./setup.sh start-all"
}

start_backend_only() {
    start_backend
}

start_frontend_only() {
    start_frontend
}

start_all_services() {
    print_step "Starting all services..."
    
    # Start backend in background
    start_backend &
    local backend_pid=$!
    
    # Start frontend in background
    start_frontend &
    local frontend_pid=$!
    
    print_info "Backend started (PID: $backend_pid)"
    print_info "Frontend started (PID: $frontend_pid)"
    print_info "Press Ctrl+C to stop all services"
    
    # Wait for both processes
    wait $backend_pid $frontend_pid
}

show_help() {
    echo -e "${BOLD}Usage:${NC} ./setup.sh [command]"
    echo ""
    echo -e "${BOLD}Commands:${NC}"
    echo "  setup         Set up the entire project (backend + frontend)"
    echo "  setup-backend Set up only the backend"
    echo "  setup-frontend Set up only the frontend"
    echo "  start-backend Start the backend development server"
    echo "  start-frontend Start the frontend development server"
    echo "  start-all     Start both backend and frontend servers"
    echo "  help          Show this help message"
    echo ""
    echo -e "${BOLD}Examples:${NC}"
    echo "  ./setup.sh setup"
    echo "  ./setup.sh start-backend"
    echo "  ./setup.sh start-frontend"
}

# ============================================================================
# Script Entry Point
# ============================================================================

main() {
    local command="${1:-setup}"
    
    case "$command" in
        "setup")
            setup_all
            ;;
        "setup-backend")
            setup_backend
            ;;
        "setup-frontend")
            setup_frontend
            ;;
        "start-backend")
            start_backend_only
            ;;
        "start-frontend")
            start_frontend_only
            ;;
        "start-all")
            start_all_services
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
