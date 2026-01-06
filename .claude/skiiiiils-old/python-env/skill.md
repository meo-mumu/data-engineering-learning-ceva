---
name: python-env
description: Manage Python environments using uv, venv, and pyproject.toml for dependency management
---

# Python Environment Management Skill

## Overview

This skill manages Python virtual environments and dependencies using modern tools:
- **uv** - Ultra-fast Python package installer and resolver
- **venv** - Standard Python virtual environment
- **pyproject.toml** - Modern dependency management (PEP 621)

## When to Use This Skill

Use this skill whenever you need to:
- Set up a Python environment for a project
- Install dependencies for Python scripts
- Add new packages to a project
- Ensure reproducible environments
- Generate or update dependency specifications

## Prerequisites

### Check if uv is installed

```bash
uv --version
```

### Install uv (if not present)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or on Linux/macOS:
```bash
pip install uv
```

## Core Operations

### 1. Initialize a New Python Project

**Create project structure with pyproject.toml:**

```bash
# Create project directory if needed
mkdir -p <project-dir>
cd <project-dir>

# Initialize with uv
uv init
```

This creates:
- `pyproject.toml` - Project metadata and dependencies
- `.python-version` - Python version specification
- Basic project structure

**Manual pyproject.toml template (if uv init not used):**

```toml
[project]
name = "project-name"
version = "0.1.0"
description = "Project description"
requires-python = ">=3.10"
dependencies = [
    # Runtime dependencies will be added here
]

[project.optional-dependencies]
dev = [
    # Development dependencies
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 2. Create Virtual Environment

**Using uv (recommended):**

```bash
# Create venv in .venv directory
uv venv

# Or specify Python version
uv venv --python 3.11
```

**Using standard venv:**

```bash
python3 -m venv .venv
```

**Activate the environment:**

```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install Dependencies

**From pyproject.toml:**

```bash
# Install all dependencies
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"
```

**Sync environment to match pyproject.toml exactly:**

```bash
uv pip sync pyproject.toml
```

### 4. Add New Dependencies

**Add a package:**

```bash
# Add to dependencies
uv add <package-name>

# Add with version constraint
uv add "pandas>=2.0.0"

# Add as dev dependency
uv add --dev pytest

# Add multiple packages
uv add requests pandas numpy
```

**Manual addition to pyproject.toml:**

```toml
[project]
dependencies = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "streamlit>=1.28.0",
    "plotly>=5.17.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]
```

Then install:
```bash
uv pip install -e ".[dev]"
```

### 5. Remove Dependencies

```bash
# Remove a package
uv remove <package-name>

# Or manually edit pyproject.toml and sync
uv pip sync
```

### 6. Lock Dependencies

**Generate uv.lock (lock file):**

```bash
uv lock
```

**Install from lock file:**

```bash
uv sync
```

### 7. Update Dependencies

```bash
# Update all dependencies
uv lock --upgrade

# Update specific package
uv lock --upgrade-package <package-name>
```

## Common Workflows

### Workflow 1: New Project Setup

```bash
# 1. Create project directory
mkdir -p my-project
cd my-project

# 2. Initialize with uv
uv init

# 3. Create virtual environment
uv venv

# 4. Activate environment
source .venv/bin/activate

# 5. Add dependencies
uv add pandas numpy streamlit plotly

# 6. Add dev dependencies
uv add --dev pytest black ruff

# 7. Lock dependencies
uv lock

# Project is ready!
```

### Workflow 2: Clone Existing Project

```bash
# 1. Clone repository
git clone <repo-url>
cd <project-dir>

# 2. Create virtual environment
uv venv

# 3. Activate environment
source .venv/bin/activate

# 4. Sync dependencies from lock file
uv sync

# Or if no lock file, install from pyproject.toml
uv pip install -e ".[dev]"
```

### Workflow 3: Add Dependencies to Existing Project

```bash
# 1. Ensure venv is activated
source .venv/bin/activate

# 2. Add new package
uv add <package-name>

# 3. Update lock file
uv lock

# 4. Sync environment
uv sync
```

### Workflow 4: Data Analysis Project (like data-analyst)

```bash
# 1. Navigate to project
cd data-analyst

# 2. Create pyproject.toml
cat > pyproject.toml << 'EOF'
[project]
name = "data-analyst"
version = "0.1.0"
description = "Data analysis with profiling and visualization"
requires-python = ">=3.10"
dependencies = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "streamlit>=1.28.0",
    "plotly>=5.17.0",
    "scipy>=1.11.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "ipython>=8.12.0",
]
EOF

# 3. Create venv
uv venv

# 4. Activate venv
source .venv/bin/activate

# 5. Install dependencies
uv pip install -e .

# 6. Lock dependencies for reproducibility
uv lock

# Ready to run!
```

## Best Practices

### 1. Always Use Virtual Environments
```bash
# Never install packages globally
# Always create and activate venv first
uv venv
source .venv/bin/activate
```

### 2. Use pyproject.toml for All Projects
- Centralizes project metadata
- Modern standard (PEP 621)
- Better than requirements.txt
- Supports optional dependencies

### 3. Pin Versions Appropriately
```toml
# Good - flexible but safe
dependencies = [
    "pandas>=2.0.0,<3.0.0",
    "numpy>=1.24.0",
]

# Avoid - too loose
dependencies = [
    "pandas",  # Any version - risky!
]

# Avoid - too strict (unless necessary)
dependencies = [
    "pandas==2.0.3",  # Exact version - limits updates
]
```

### 4. Separate Dev and Runtime Dependencies
```toml
[project]
dependencies = [
    # Only runtime dependencies
    "pandas>=2.0.0",
    "streamlit>=1.28.0",
]

[project.optional-dependencies]
dev = [
    # Testing, linting, etc.
    "pytest>=7.4.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]
```

### 5. Lock Dependencies for Reproducibility
```bash
# After adding/updating dependencies
uv lock

# Commit uv.lock to version control
git add uv.lock
git commit -m "Lock dependencies"
```

### 6. Use .gitignore
```
# .gitignore
.venv/
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
```

## Troubleshooting

### uv command not found
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or
pip install uv
```

### Virtual environment not activating
```bash
# Make sure you're in the right directory
cd <project-dir>

# Try explicit path
source .venv/bin/activate

# Check if venv exists
ls -la .venv/
```

### Dependencies not installing
```bash
# Clear cache and retry
uv cache clean
uv pip install -e .

# Check Python version compatibility
python --version
# Should match requires-python in pyproject.toml
```

### Conflicts between dependencies
```bash
# Let uv resolve
uv lock --upgrade

# Or update conflicting package
uv add "package-name>=newer-version"
```

## Quick Reference

| Task | Command |
|------|---------|
| Install uv | `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Create venv | `uv venv` |
| Activate venv | `source .venv/bin/activate` |
| Add package | `uv add <package>` |
| Add dev package | `uv add --dev <package>` |
| Install from pyproject.toml | `uv pip install -e .` |
| Install with dev deps | `uv pip install -e ".[dev]"` |
| Lock dependencies | `uv lock` |
| Sync from lock | `uv sync` |
| Update all deps | `uv lock --upgrade` |
| Remove package | `uv remove <package>` |
| List installed | `uv pip list` |
| Show package info | `uv pip show <package>` |

## Integration with Agents

When an agent (like data-analyst) needs Python dependencies:

1. **Check if venv exists** in agent's working directory
2. **Create venv** if missing: `uv venv`
3. **Create/update pyproject.toml** with required dependencies
4. **Install dependencies**: `uv pip install -e .`
5. **Lock for reproducibility**: `uv lock`

Example for data-analyst:
```bash
cd data-analyst

# Ensure pyproject.toml exists with dependencies
# Create venv
uv venv

# Activate (for interactive use)
source .venv/bin/activate

# Install
uv pip install -e .

# Run with venv python
.venv/bin/python analyze.py
.venv/bin/streamlit run app.py
```

## Remember

- **uv is fast** - 10-100x faster than pip
- **pyproject.toml is standard** - Modern Python packaging
- **Lock files ensure reproducibility** - Always commit uv.lock
- **Separate dev deps** - Keep runtime lean
- **Use venv always** - Never pollute global Python
- **Activate before running** - Ensure correct environment

---

*Ready to manage Python environments efficiently with uv!*
