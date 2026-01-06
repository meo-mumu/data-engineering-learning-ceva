---
name: python-env-uv
description: Setup and manage Python environments using uv. Initialize projects, create virtual environments, install packages, and manage dependencies with pyproject.toml. Use when setting up new Python projects or managing dependencies.
---

# Python Environment Management with uv

Complete toolkit for managing Python projects using `uv` - the fast Python package installer and environment manager.

## What This Skill Does

- Initialize Python projects with pyproject.toml
- Create isolated virtual environments
- Install and manage packages
- Track dependencies with pyproject.toml
- Verify installations
- Create standard data project structures

## Core Commands

### 1. Initialize Project

```bash
# Initialize new project with Python 3.13
uv init --name project-name --python 3.13

# Creates:
# - pyproject.toml
# - README.md
# - .python-version
```

### 2. Create Virtual Environment

```bash
# Create .venv with Python 3.13
uv venv --python 3.13

# Activation command (for reference):
# source .venv/bin/activate
```

### 3. Add Packages

```bash
# Add single package
uv add package-name

# Add with version constraint
uv add "package-name>=1.0.0"

# Add multiple packages
uv add pandas numpy matplotlib

# Add development dependencies
uv add --dev pytest black
```

### 4. Install Dependencies

```bash
# Install all dependencies from pyproject.toml
uv sync

# Install and update
uv sync --upgrade
```

### 5. List Installed Packages

```bash
# Show all installed packages
uv pip list

# Show as JSON
uv pip list --format=json
```

### 6. Verify Installation

```bash
# Test import in isolated environment
uv run python -c "import package_name; print(package_name.__version__)"

# Run script with uv
uv run python script.py

# Run streamlit with uv
uv run streamlit run app.py
```

## Common Workflows

### New Data Project Setup

```bash
# 1. Initialize project
uv init --name my-data-project --python 3.13

# 2. Create virtual environment
uv venv --python 3.13

# 3. Add data science packages
uv add pandas numpy matplotlib seaborn plotly streamlit scikit-learn

# 4. Verify installations
uv run python -c "import pandas; import numpy; import streamlit; print('✓ All packages ready')"
```

### Add Package to Existing Project

```bash
# 1. Add the package (updates pyproject.toml automatically)
uv add new-package

# 2. Sync environment
uv sync

# 3. Verify
uv run python -c "import new_package"
```

### Reproduce Environment from pyproject.toml

```bash
# 1. Clone/copy project with pyproject.toml
cd project-directory

# 2. Create venv
uv venv --python 3.13

# 3. Install all dependencies
uv sync

# Done! All packages from pyproject.toml are installed
```

## Standard Data Project Structure

```bash
project/
├── .venv/                 # Virtual environment (created by uv venv)
├── data/
│   ├── raw/              # Original, immutable data
│   ├── processed/        # Cleaned, transformed data
│   └── output/           # Analysis results, exports
├── notebooks/            # Jupyter notebooks for exploration
├── src/                  # Source code modules
├── tests/                # Test files
├── docs/                 # Documentation
├── pyproject.toml        # Dependencies and project config
├── .python-version       # Python version for the project
└── README.md            # Project documentation
```

### Create Structure

```bash
mkdir -p data/{raw,processed,output} notebooks src tests docs
```

## Usage Examples

### Example 1: Streamlit Dashboard Project

```bash
# Setup
uv init --name dashboard --python 3.13
uv venv --python 3.13
uv add streamlit pandas plotly

# Create structure
mkdir -p data/raw src

# Run dashboard
uv run streamlit run src/dashboard.py
```

### Example 2: Data Analysis Project

```bash
# Setup
uv init --name analysis --python 3.13
uv venv --python 3.13
uv add pandas numpy matplotlib seaborn jupyter

# Create notebooks
mkdir notebooks

# Launch jupyter
uv run jupyter notebook
```

### Example 3: ML Pipeline

```bash
# Setup
uv init --name ml-pipeline --python 3.13
uv venv --python 3.13
uv add pandas numpy scikit-learn mlflow

# Add dev tools
uv add --dev pytest black mypy

# Structure
mkdir -p data/{raw,processed} src/models src/features tests
```

## Key Files

### pyproject.toml

Automatically managed by uv. Example:

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "pandas>=2.3.3",
    "numpy>=2.3.5",
    "streamlit>=1.52.2",
]
```

### .python-version

Specifies Python version:

```
3.13
```

## Best Practices

1. **Always specify Python version** - Use `--python 3.13` for consistency
2. **Use version constraints** - `uv add "package>=1.0"` for stability
3. **Separate dev dependencies** - Use `--dev` flag for development tools
4. **Run via uv** - Use `uv run` to ensure correct environment
5. **Commit pyproject.toml** - Version control your dependencies
6. **Ignore .venv** - Add to `.gitignore`

## Troubleshooting

### Package not found after install

```bash
# Make sure to sync after adding
uv add package-name
uv sync
```

### Import fails

```bash
# Always run via uv to use correct environment
uv run python script.py

# Not just: python script.py
```

### Wrong Python version

```bash
# Check version
uv run python --version

# Recreate venv with correct version
rm -rf .venv
uv venv --python 3.13
uv sync
```

## Quick Reference

| Task | Command |
|------|---------|
| Init project | `uv init --python 3.13` |
| Create venv | `uv venv --python 3.13` |
| Add package | `uv add package` |
| Install all | `uv sync` |
| List packages | `uv pip list` |
| Run script | `uv run python script.py` |
| Run streamlit | `uv run streamlit run app.py` |
| Test import | `uv run python -c "import pkg"` |

## Integration with Other Tools

### With Git

```bash
# .gitignore
.venv/
__pycache__/
*.pyc
.python-version
```

### With Docker

```dockerfile
FROM python:3.13-slim
COPY pyproject.toml .
RUN pip install uv
RUN uv sync
```

### With CI/CD

```yaml
# GitHub Actions example
- name: Setup Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.13'

- name: Install uv
  run: pip install uv

- name: Install dependencies
  run: uv sync
```

---

**Remember:** This skill provides tools and commands. Decision-making about which packages to install or when to setup environments should come from agents or the orchestrator.
