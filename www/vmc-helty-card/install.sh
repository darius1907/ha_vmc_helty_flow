#!/bin/bash
# VMC Helty Card - Installation Script
# Automatic installation for Home Assistant

set -e

# Configuration
CARD_NAME="vmc-helty-card"
HA_CONFIG_DIR="/config"
WWW_DIR="$HA_CONFIG_DIR/www"
CARD_DIR="$WWW_DIR/$CARD_NAME"
LOVELACE_CONFIG="$HA_CONFIG_DIR/ui-lovelace.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in Home Assistant environment
check_environment() {
    log_info "Checking Home Assistant environment..."

    if [ ! -d "$HA_CONFIG_DIR" ]; then
        log_error "Home Assistant config directory not found: $HA_CONFIG_DIR"
        log_info "Please run this script from within Home Assistant or update HA_CONFIG_DIR variable"
        exit 1
    fi

    log_success "Home Assistant environment detected"
}

# Create directories
create_directories() {
    log_info "Creating directories..."

    mkdir -p "$WWW_DIR"
    mkdir -p "$CARD_DIR"

    log_success "Directories created successfully"
}

# Copy card files
install_files() {
    log_info "Installing VMC Helty Card files..."

    # Check if files exist in current directory
    if [ ! -f "vmc-helty-card.js" ]; then
        log_error "vmc-helty-card.js not found in current directory"
        exit 1
    fi

    if [ ! -f "vmc-helty-card-editor.js" ]; then
        log_error "vmc-helty-card-editor.js not found in current directory"
        exit 1
    fi

    # Copy files
    cp vmc-helty-card.js "$CARD_DIR/"
    cp vmc-helty-card-editor.js "$CARD_DIR/"

    # Copy documentation (optional)
    [ -f "README.md" ] && cp README.md "$CARD_DIR/"
    [ -f "QUICK-START.md" ] && cp QUICK-START.md "$CARD_DIR/"
    [ -f "examples.yaml" ] && cp examples.yaml "$CARD_DIR/"
    [ -f "LICENSE" ] && cp LICENSE "$CARD_DIR/"

    log_success "Files installed successfully to $CARD_DIR"
}

# Add resource to Lovelace
add_lovelace_resource() {
    log_info "Checking Lovelace configuration..."

    RESOURCE_URL="/local/$CARD_NAME/vmc-helty-card.js"

    # Check if resource already exists
    if [ -f "$LOVELACE_CONFIG" ]; then
        if grep -q "$RESOURCE_URL" "$LOVELACE_CONFIG"; then
            log_warning "Resource already exists in $LOVELACE_CONFIG"
            return
        fi

        # Add resource to existing file
        log_info "Adding resource to existing Lovelace configuration..."

        # Create backup
        cp "$LOVELACE_CONFIG" "$LOVELACE_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"

        # Check if resources section exists
        if grep -q "^resources:" "$LOVELACE_CONFIG"; then
            # Add to existing resources section
            sed -i "/^resources:/a\\  - url: $RESOURCE_URL\\n    type: module" "$LOVELACE_CONFIG"
        else
            # Add new resources section at the beginning
            {
                echo "resources:"
                echo "  - url: $RESOURCE_URL"
                echo "    type: module"
                echo ""
                cat "$LOVELACE_CONFIG"
            } > "$LOVELACE_CONFIG.tmp" && mv "$LOVELACE_CONFIG.tmp" "$LOVELACE_CONFIG"
        fi

        log_success "Resource added to Lovelace configuration"
    else
        log_warning "Lovelace configuration file not found"
        log_info "Please add the following to your Lovelace resources:"
        echo ""
        echo "resources:"
        echo "  - url: $RESOURCE_URL"
        echo "    type: module"
        echo ""
    fi
}

# Set correct permissions
set_permissions() {
    log_info "Setting file permissions..."

    chmod 644 "$CARD_DIR"/*.js
    [ -f "$CARD_DIR/README.md" ] && chmod 644 "$CARD_DIR/README.md"
    [ -f "$CARD_DIR/QUICK-START.md" ] && chmod 644 "$CARD_DIR/QUICK-START.md"
    [ -f "$CARD_DIR/examples.yaml" ] && chmod 644 "$CARD_DIR/examples.yaml"

    log_success "Permissions set successfully"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."

    # Check files exist
    [ -f "$CARD_DIR/vmc-helty-card.js" ] || { log_error "vmc-helty-card.js not found"; exit 1; }
    [ -f "$CARD_DIR/vmc-helty-card-editor.js" ] || { log_error "vmc-helty-card-editor.js not found"; exit 1; }

    # Check file sizes (basic sanity check)
    [ -s "$CARD_DIR/vmc-helty-card.js" ] || { log_error "vmc-helty-card.js is empty"; exit 1; }
    [ -s "$CARD_DIR/vmc-helty-card-editor.js" ] || { log_error "vmc-helty-card-editor.js is empty"; exit 1; }

    log_success "Installation verified successfully"
}

# Main installation function
main() {
    echo ""
    log_info "🌀 VMC Helty Card Installation Script"
    log_info "======================================"
    echo ""

    check_environment
    create_directories
    install_files
    add_lovelace_resource
    set_permissions
    verify_installation

    echo ""
    log_success "🎉 VMC Helty Card installed successfully!"
    echo ""
    log_info "Next steps:"
    echo "  1. Restart Home Assistant"
    echo "  2. Clear browser cache (Ctrl+F5)"
    echo "  3. Go to Lovelace dashboard"
    echo "  4. Click 'Add Card' and search for 'VMC Helty'"
    echo "  5. Configure your VMC device and sensors"
    echo ""
    log_info "📚 Documentation available at: $CARD_DIR/README.md"
    log_info "🚀 Quick start guide: $CARD_DIR/QUICK-START.md"
    log_info "📋 Configuration examples: $CARD_DIR/examples.yaml"
    echo ""
}

# Run installation
main "$@"
