# Testing Guide for zaepho.zohobooks

This guide explains how to test the `zaepho.zohobooks` Ansible collection locally before submitting pull requests.

## Quick Start

The easiest way to run tests is using the provided Makefile:

```bash
# Run sanity tests (linting, documentation validation)
make sanity

# Build the collection
make build

# Build and view documentation
make docs

# Run all tests
make all-tests
```

## Test Script

We provide a comprehensive test script `test.sh` that mirrors the GitHub Actions CI workflow:

### Basic Usage

```bash
# Run sanity tests (default)
./test.sh

# Show help
./test.sh --help

# Run all tests
./test.sh all

# Run specific test type
./test.sh sanity          # Linting and validation
./test.sh units           # Unit tests
./test.sh integration     # Integration tests
./test.sh build           # Build collection
./test.sh docs            # Build documentation
```

### Advanced Usage

```bash
# Test with specific Ansible version
./test.sh sanity stable-2.17

# Test with specific Python version
./test.sh integration stable-2.16 3.10

# Verbose output
VERBOSE=true ./test.sh sanity
```

## Test Types

### 1. Sanity Tests

Sanity tests validate code quality, documentation, and Ansible best practices.

**Run sanity tests:**
```bash
make sanity
# or
./test.sh sanity
```

**What it checks:**
- Python syntax and style (pylint, pep8)
- Module documentation (validate-modules)
- Ansible-specific issues (ansible-doc)
- Import errors
- YAML syntax
- And more...

**Common issues:**
- Missing or incorrect DOCUMENTATION
- Invalid return value keys (like `items`)
- PEP8 style violations
- Import errors

### 2. Unit Tests

Unit tests test individual functions and classes in isolation.

**Run unit tests:**
```bash
make units
# or
./test.sh units
```

**Note:** Currently, there are no unit tests in this collection. Unit tests would be added in `tests/units/` directory.

### 3. Integration Tests

Integration tests test modules end-to-end with actual API calls (or mocked services).

**Run integration tests:**
```bash
make integration
# or
./test.sh integration
```

**Note:** Currently, there are no integration tests in this collection. Integration tests would be added in `tests/integration/targets/` directory.

### 4. Documentation Tests

Build and validate the documentation.

**Run documentation tests:**
```bash
make docs
# or
./test.sh docs
```

**View documentation locally:**
```bash
make docs-serve
# Opens at http://localhost:8000
```

## GitHub Actions CI

All tests run automatically via GitHub Actions when you:
- Push to the `main` branch
- Open a pull request
- Daily scheduled runs

The CI workflow is defined in `.github/workflows/ansible-test.yml` and tests against multiple:
- Ansible versions (2.16, 2.17, 2.18, devel)
- Python versions (3.6 - 3.13)

## Prerequisites

### Required Tools

- Python 3.6 or higher
- Ansible Core 2.16 or higher
- Docker (for ansible-test)

### Installation

```bash
# Install Ansible
pip install ansible-core

# Install test dependencies
pip install -r docs/requirements.txt

# Install antsibull-changelog (for changelog generation)
pip install antsibull-changelog
```

## Continuous Integration

### Sanity Tests Matrix

Tested against:
- ansible-core stable-2.16
- ansible-core stable-2.17
- ansible-core stable-2.18
- ansible-core devel

### Integration Tests Matrix

Tested against multiple combinations of:
- Ansible versions: 2.16, 2.17, 2.18, devel
- Python versions: 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13

## Common Issues and Solutions

### Issue: ansible-test requires collection to be in specific path

**Solution:** The `test.sh` script automatically sets up the correct directory structure.

### Issue: Docker not available

**Solution:** Install Docker or use the `--local` flag with ansible-test (not recommended for consistency).

### Issue: Sanity test failures about return value keys

**Solution:** Avoid using return value keys that conflict with Python built-ins or dict methods:
- Bad: `items`, `keys`, `values`, `get`, `update`
- Good: `zohobooks_items`, `account_list`, `results`

### Issue: Module documentation validation errors

**Solution:** Ensure DOCUMENTATION, EXAMPLES, and RETURN are properly formatted:
- Don't include `no_log: true` in DOCUMENTATION (only in argument_spec)
- Use proper YAML formatting
- Follow the module documentation schema

## Writing Tests

### Adding Unit Tests

Create tests in `tests/units/plugins/modules/`:

```python
# tests/units/plugins/modules/test_zohobooks_account.py
from ansible_collections.zaepho.zohobooks.plugins.modules import zohobooks_account

def test_something():
    # Your test here
    pass
```

### Adding Integration Tests

Create test playbooks in `tests/integration/targets/zohobooks_account/`:

```yaml
# tests/integration/targets/zohobooks_account/tasks/main.yml
---
- name: Test creating an account
  zaepho.zohobooks.zohobooks_account:
    name: "Test Account"
    account_type: "bank"
    state: present
  register: result

- name: Verify account was created
  assert:
    that:
      - result.changed
      - result.account.account_name == "Test Account"
```

## Before Submitting a PR

Run this checklist:

```bash
# 1. Run sanity tests
make sanity

# 2. Build collection
make build

# 3. Build documentation
make docs

# 4. Ensure changelog fragment exists (if needed)
ls changelogs/fragments/

# 5. Clean up
make clean
```

## Makefile Targets Reference

| Target | Description |
|--------|-------------|
| `help` | Show all available targets |
| `build` | Build collection tarball |
| `install` | Build and install collection locally |
| `test` | Run default tests (sanity) |
| `sanity` | Run sanity tests |
| `units` | Run unit tests |
| `integration` | Run integration tests |
| `all-tests` | Run all tests |
| `docs` | Build documentation |
| `docs-serve` | Build and serve docs at http://localhost:8000 |
| `clean` | Remove build artifacts |
| `changelog` | Generate changelog from fragments |
| `release` | Prepare a release |
| `validate` | Validate collection structure |
| `all` | Run all tasks |

## Additional Resources

- [Ansible Collection Testing Guide](https://docs.ansible.com/ansible/latest/dev_guide/testing_collections.html)
- [ansible-test Documentation](https://docs.ansible.com/ansible/latest/dev_guide/testing.html)
- [Collection Requirements](https://docs.ansible.com/ansible/latest/community/collection_contributors/collection_requirements.html)
- [Module Development Guide](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)

## Getting Help

If you encounter issues:

1. Check the [GitHub Issues](https://github.com/zaepho-org/ansible_collection_zohobooks/issues)
2. Review the [CI logs](.github/workflows/ansible-test.yml)
3. Consult the [Ansible Community Documentation](https://docs.ansible.com/ansible/devel/community/index.html)
