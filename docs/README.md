# Documentation for zaepho.zohobooks

This directory contains the documentation source and build system for the `zaepho.zohobooks` Ansible collection.

## Building Documentation Locally

### Prerequisites

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### Build Steps

1. Build the collection:
   ```bash
   cd ..
   ansible-galaxy collection build --force
   ```

2. Install the collection locally:
   ```bash
   ansible-galaxy collection install zaepho-zohobooks-*.tar.gz --force
   ```

3. Build the documentation:
   ```bash
   cd docs
   bash build.sh
   ```

4. View the documentation:
   ```bash
   # Open docs/build/html/index.html in your browser
   firefox build/html/index.html  # or your preferred browser
   ```

## Documentation Structure

- **`antsibull-docs.cfg`**: Configuration for antsibull-docs tool
- **`conf.py`**: Sphinx configuration file
- **`requirements.txt`**: Python dependencies for building docs
- **`build.sh`**: Build script that runs antsibull-docs and Sphinx
- **`rst/index.rst`**: Main documentation index page (manually maintained)
- **`docsite/links.yml`**: Configuration for Edit on GitHub links and extra links

## Generated Files

The following files are automatically generated and should not be manually edited:

- `rst/collections/` - Generated collection documentation
- `rst/zohobooks_*.rst` - Generated module documentation
- `rst/environment_variables.rst` - Generated environment variables index
- `build/` - HTML output directory

## Automated Builds

Documentation is automatically built and deployed to GitHub Pages via GitHub Actions:

- **On push to main**: Docs are built and deployed to GitHub Pages
- **On pull requests**: Docs are built to verify no errors (but not deployed)
- **Manual trigger**: Can be triggered manually via GitHub Actions UI

## Viewing Published Documentation

Once deployed, the documentation will be available at:
https://zaepho-org.github.io/ansible_collection_zohobooks/

## Customization

### Updating the Main Index

Edit `rst/index.rst` to customize the main documentation page.

### Updating Links and Metadata

Edit `docsite/links.yml` to customize:
- Edit on GitHub links
- Extra navigation links
- Communication channels

### Updating Sphinx Theme

Edit `conf.py` to customize the Sphinx theme and configuration.
