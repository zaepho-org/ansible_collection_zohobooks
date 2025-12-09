.PHONY: help build install test sanity shellcheck units integration docs clean all

# Variables
COLLECTION_NAMESPACE := zaepho
COLLECTION_NAME := zohobooks
COLLECTION_VERSION := $(shell grep '^version:' galaxy.yml | awk '{print $$2}')
COLLECTION_TARBALL := $(COLLECTION_NAMESPACE)-$(COLLECTION_NAME)-$(COLLECTION_VERSION).tar.gz

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the collection tarball
	@echo "Building collection..."
	@ansible-galaxy collection build --force
	@echo "Built: $(COLLECTION_TARBALL)"

install: build ## Build and install the collection locally
	@echo "Installing collection..."
	@ansible-galaxy collection install $(COLLECTION_TARBALL) --force
	@echo "Collection installed successfully"

test: shellcheck sanity ## Run default tests (shellcheck + sanity)
	@echo "Default tests completed"

shellcheck: ## Run shellcheck on test.sh
	@echo "Running shellcheck..."
	@shellcheck test.sh || (echo "Shellcheck failed. Install with: sudo apt-get install shellcheck" && exit 1)
	@echo "Shellcheck passed"

sanity: shellcheck ## Run sanity tests
	@echo "Running sanity tests..."
	@./test.sh sanity

units: ## Run unit tests
	@echo "Running unit tests..."
	@./test.sh units

integration: ## Run integration tests
	@echo "Running integration tests..."
	@./test.sh integration

all-tests: ## Run all tests (sanity, units, integration)
	@echo "Running all tests..."
	@./test.sh all

docs: install ## Build documentation
	@echo "Building documentation..."
	@cd docs && bash build.sh
	@echo "Documentation built: docs/build/html/index.html"

docs-serve: docs ## Build and serve documentation locally
	@echo "Serving documentation at http://localhost:8000"
	@cd docs/build/html && python3 -m http.server 8000

clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	@rm -f $(COLLECTION_NAMESPACE)-$(COLLECTION_NAME)-*.tar.gz
	@rm -rf ansible_collections
	@rm -rf docs/build
	@rm -rf docs/rst/collections
	@rm -f docs/rst/zohobooks_*.rst
	@rm -f docs/rst/environment_variables.rst
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaned successfully"

changelog: ## Generate changelog from fragments
	@echo "Generating changelog..."
	@antsibull-changelog release
	@echo "Changelog generated"

release: clean build ## Prepare a release (clean, build, changelog)
	@echo "Preparing release $(COLLECTION_VERSION)..."
	@$(MAKE) changelog
	@echo "Release $(COLLECTION_VERSION) ready"
	@echo "Tarball: $(COLLECTION_TARBALL)"

validate: build ## Validate the collection structure
	@echo "Validating collection..."
	@ansible-galaxy collection install $(COLLECTION_TARBALL) --force
	@echo "Collection validation passed"

all: clean build install test docs ## Run all tasks (clean, build, install, test, docs)
	@echo "All tasks completed successfully"
