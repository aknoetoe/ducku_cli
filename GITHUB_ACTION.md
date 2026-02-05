# Using Ducku as a GitHub Action

Ducku can be used as a GitHub Action to automatically check your documentation for outdated artifacts.

## Quick Start

Add this to your workflow file (e.g., `.github/workflows/docs-check.yml`):

```yaml
name: Documentation Check

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  ducku:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check documentation
        uses: yarax/ducku@v1
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `path` | Path to the project to analyze (relative to repo root) | No | `.` |
| `fail-on-issues` | Fail the workflow if issues are found | No | `true` |

## Examples

### Basic usage

```yaml
- uses: yarax/ducku@v1
```

### Check a specific subdirectory

```yaml
- uses: yarax/ducku@v1
  with:
    path: 'packages/my-app'
```

### Don't fail on issues (warning only)

```yaml
- uses: yarax/ducku@v1
  with:
    fail-on-issues: 'false'
```

### Full workflow example

```yaml
name: Documentation Quality

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  check-docs:
    name: Check Documentation
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Run Ducku documentation checker
        uses: yarax/ducku@v1
        with:
          fail-on-issues: 'true'
```

## What it checks

Ducku detects outdated artifacts in your documentation:

- **File paths** - Unix and Windows paths that don't exist in the project
- **Filenames** - Referenced files that are missing
- **Environment variables** - Env vars mentioned but not used in code
- **Ports** - Port numbers that may have changed
- **HTTP Routes** - API endpoints that no longer exist
- **Unused modules** - Code modules that are never imported
- **Partial matches** - Lists that have drifted between docs and code

## Configuration

You can configure Ducku by adding a `ducku.yaml` file to your project root. See the [main documentation](README.md) for configuration options.
