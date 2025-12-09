#!/usr/bin/env bash
# Test script for zaepho.zohobooks collection
# Based on GitHub Actions CI workflow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="${1:-sanity}"
ANSIBLE_VERSION="${2:-stable-2.16}"
PYTHON_VERSION="${3:-3.11}"
VERBOSE="${VERBOSE:-false}"

# Collection information
COLLECTION_NAMESPACE="zaepho"
COLLECTION_NAME="zohobooks"
COLLECTION_PATH="${HOME}/.ansible/collections/ansible_collections/${COLLECTION_NAMESPACE}/${COLLECTION_NAME}"

print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

show_usage() {
    cat << EOF
Usage: $0 [TEST_TYPE] [ANSIBLE_VERSION] [PYTHON_VERSION]

Test the zaepho.zohobooks Ansible collection locally.

Arguments:
    TEST_TYPE         Type of tests to run (default: sanity)
                      Options: sanity, units, integration, all, build, docs
    ANSIBLE_VERSION   Ansible version to test against (default: stable-2.16)
                      Options: stable-2.16, stable-2.17, stable-2.18, devel
    PYTHON_VERSION    Python version to use (default: 3.11)
                      Options: 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13

Environment Variables:
    VERBOSE           Set to 'true' for verbose output (default: false)

Examples:
    # Run sanity tests with defaults
    $0

    # Run all tests
    $0 all

    # Run sanity tests with specific Ansible version
    $0 sanity stable-2.17

    # Run integration tests with specific Python version
    $0 integration stable-2.16 3.10

    # Run with verbose output
    VERBOSE=true $0 sanity

Tests Available:
    sanity       - Run ansible-test sanity checks (linting, documentation)
    units        - Run unit tests (requires test files in tests/units/)
    integration  - Run integration tests (requires test files in tests/integration/)
    all          - Run sanity, units, and integration tests
    build        - Build the collection tarball
    docs         - Build documentation

EOF
}

check_requirements() {
    print_header "Checking Requirements"

    local missing_deps=()

    # Check for ansible-galaxy
    if ! command -v ansible-galaxy &> /dev/null; then
        missing_deps+=("ansible")
    else
        print_success "ansible-galaxy found: $(ansible-galaxy --version | head -1)"
    fi

    # Check for ansible-test
    if ! command -v ansible-test &> /dev/null; then
        missing_deps+=("ansible-test")
    else
        print_success "ansible-test found"
    fi

    # Check for Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    else
        print_success "python3 found: $(python3 --version)"
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        echo ""
        echo "Install with:"
        echo "  pip install ansible-core"
        exit 1
    fi

    echo ""
}

build_collection() {
    print_header "Building Collection"

    # Clean old builds
    rm -f ${COLLECTION_NAMESPACE}-${COLLECTION_NAME}-*.tar.gz

    # Build collection
    if ansible-galaxy collection build --force; then
        print_success "Collection built successfully"
        ls -lh ${COLLECTION_NAMESPACE}-${COLLECTION_NAME}-*.tar.gz
    else
        print_error "Failed to build collection"
        exit 1
    fi

    echo ""
}

install_collection() {
    print_header "Installing Collection"

    # Install collection to proper location for ansible-test
    if ansible-galaxy collection install ${COLLECTION_NAMESPACE}-${COLLECTION_NAME}-*.tar.gz --force; then
        print_success "Collection installed to ${COLLECTION_PATH}"
    else
        print_error "Failed to install collection"
        exit 1
    fi

    echo ""
}

setup_test_environment() {
    print_header "Setting Up Test Environment"

    # Create ansible_collections directory structure in the current directory
    local test_collections_dir="./ansible_collections/${COLLECTION_NAMESPACE}/${COLLECTION_NAME}"

    if [ -d "ansible_collections" ]; then
        print_info "Removing old ansible_collections directory"
        rm -rf ansible_collections
    fi

    print_info "Creating test collections directory structure"
    mkdir -p "$test_collections_dir"

    # Copy collection files to test location
    print_info "Copying collection files to test location"
    rsync -av --exclude='ansible_collections' \
              --exclude='*.tar.gz' \
              --exclude='.git' \
              --exclude='__pycache__' \
              --exclude='*.pyc' \
              --exclude='docs/build' \
              --exclude='docs/rst/collections' \
              --exclude='docs/rst/zohobooks_*.rst' \
              --exclude='docs/rst/environment_variables.rst' \
              ./ "$test_collections_dir/"

    print_success "Test environment ready at $test_collections_dir"
    echo ""
}

run_sanity_tests() {
    print_header "Running Sanity Tests"

    setup_test_environment

    cd "ansible_collections/${COLLECTION_NAMESPACE}/${COLLECTION_NAME}"

    # Try docker first, fall back to local if docker fails
    local cmd="ansible-test sanity --docker default"

    if [ "$VERBOSE" = "true" ]; then
        cmd="$cmd -v"
    fi

    print_info "Attempting to run with Docker: $cmd"
    echo ""

    # Run and capture output and exit code
    set +e
    eval "$cmd" > /tmp/ansible-test-output.log 2>&1
    local docker_exit_code=$?
    set -e

    # Check if docker/podman is the issue
    if [ $docker_exit_code -ne 0 ] && grep -q "Failed to run docker image\|podman\|netavark\|nftables" /tmp/ansible-test-output.log 2>/dev/null; then
        cat /tmp/ansible-test-output.log
        print_warning "Docker/Podman networking failed, retrying with --local mode"
        echo ""

        local local_cmd="ansible-test sanity --local"
        if [ "$VERBOSE" = "true" ]; then
            local_cmd="$local_cmd -v"
        fi

        print_info "Running: $local_cmd"
        echo ""

        if eval "$local_cmd"; then
            print_success "Sanity tests passed (local mode)"
            cd - > /dev/null
            return 0
        else
            print_error "Sanity tests failed"
            cd - > /dev/null
            return 1
        fi
    elif [ $docker_exit_code -eq 0 ]; then
        cat /tmp/ansible-test-output.log
        print_success "Sanity tests passed"
        cd - > /dev/null
        return 0
    else
        cat /tmp/ansible-test-output.log
        print_error "Sanity tests failed"
        cd - > /dev/null
        return 1
    fi
}

run_units_tests() {
    print_header "Running Unit Tests"

    setup_test_environment

    cd "ansible_collections/${COLLECTION_NAMESPACE}/${COLLECTION_NAME}"

    # Check if unit tests exist
    local has_tests=false
    if compgen -G "tests/units/*.py" > /dev/null 2>&1; then
        has_tests=true
    fi

    if [ "$has_tests" = false ]; then
        print_warning "No unit tests found in tests/units/"
        print_info "Skipping unit tests"
        cd - > /dev/null
        return 0
    fi

    local cmd="ansible-test units --docker default --python ${PYTHON_VERSION}"

    if [ "$VERBOSE" = "true" ]; then
        cmd="$cmd -v"
    fi

    print_info "Running: $cmd"
    echo ""

    if eval "$cmd"; then
        print_success "Unit tests passed"
        cd - > /dev/null
        return 0
    else
        print_error "Unit tests failed"
        cd - > /dev/null
        return 1
    fi
}

run_integration_tests() {
    print_header "Running Integration Tests"

    setup_test_environment

    cd "ansible_collections/${COLLECTION_NAMESPACE}/${COLLECTION_NAME}"

    # Check if integration tests exist
    local has_tests=false
    if [ -d tests/integration/targets/ ]; then
        for file in tests/integration/targets/*; do
            if [ -e "$file" ] && [ "$(basename "$file")" != ".gitkeep" ]; then
                has_tests=true
                break
            fi
        done
    fi

    if [ "$has_tests" = false ]; then
        print_warning "No integration tests found in tests/integration/targets/"
        print_info "Skipping integration tests"
        cd - > /dev/null
        return 0
    fi

    local cmd="ansible-test integration --docker default --python ${PYTHON_VERSION}"

    if [ "$VERBOSE" = "true" ]; then
        cmd="$cmd -v"
    fi

    print_info "Running: $cmd"
    echo ""

    if eval "$cmd"; then
        print_success "Integration tests passed"
        cd - > /dev/null
        return 0
    else
        print_error "Integration tests failed"
        cd - > /dev/null
        return 1
    fi
}

build_docs() {
    print_header "Building Documentation"

    if [ ! -d "docs" ]; then
        print_error "docs directory not found"
        return 1
    fi

    # Build collection first
    build_collection

    # Install collection
    if ansible-galaxy collection install ${COLLECTION_NAMESPACE}-${COLLECTION_NAME}-*.tar.gz --force; then
        print_success "Collection installed for documentation build"
    else
        print_error "Failed to install collection"
        return 1
    fi

    # Build docs
    cd docs
    if bash build.sh; then
        print_success "Documentation built successfully"
        print_info "Documentation available at: docs/build/html/index.html"
        cd ..
        return 0
    else
        print_error "Documentation build failed"
        cd ..
        return 1
    fi
}

cleanup() {
    print_info "Cleaning up test environment"
    rm -rf ansible_collections
}

# Main script
main() {
    # Show usage if requested
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
        exit 0
    fi

    print_header "Zoho Books Collection Test Suite"
    echo "Test Type: $TEST_TYPE"
    echo "Ansible Version: $ANSIBLE_VERSION"
    echo "Python Version: $PYTHON_VERSION"
    echo ""

    # Check requirements
    check_requirements

    # Track test results
    local failed_tests=()

    # Run tests based on type
    case "$TEST_TYPE" in
        sanity)
            run_sanity_tests || failed_tests+=("sanity")
            ;;
        units)
            run_units_tests || failed_tests+=("units")
            ;;
        integration)
            run_integration_tests || failed_tests+=("integration")
            ;;
        all)
            run_sanity_tests || failed_tests+=("sanity")
            run_units_tests || failed_tests+=("units")
            run_integration_tests || failed_tests+=("integration")
            ;;
        build)
            build_collection || failed_tests+=("build")
            ;;
        docs)
            build_docs || failed_tests+=("docs")
            ;;
        *)
            print_error "Unknown test type: $TEST_TYPE"
            echo ""
            show_usage
            exit 1
            ;;
    esac

    # Cleanup
    cleanup

    # Print summary
    echo ""
    print_header "Test Summary"

    if [ ${#failed_tests[@]} -eq 0 ]; then
        print_success "All tests passed!"
        exit 0
    else
        print_error "Some tests failed: ${failed_tests[*]}"
        exit 1
    fi
}

# Run main function
main "$@"
