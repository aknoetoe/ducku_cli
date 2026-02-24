# Ducku 

Ducku is a static documentation quality tool

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-DSAL-orange.svg)](LICENSE)

[ This documentation was checked by Ducku ]

**Ducku** is a documentation analysis and code quality CLI tool designed to help developers maintain clean, consistent, and up-to-date codebases. It automatically scans projects to identify issues like outdated documentation references, unused modules, and inconsistencies between code and documentation.

## 🚀 Use Cases

### 1. Pattern Search 🔍

Often documentation contains some outdated artifacts, like non-existing scripts and ports which have been changed.
Ducku statically detects certain patterns in documentation and checks their existence in the code.
Currently it supports:

- Filenames
- File paths (both Unix and Windows)
- Environment variables
- Ports
- HTTP Routes



### 3. Partial Match Detection 🎯

Second frequent issue in documentation is partial lists. For example in this project there can be implemented a new use case, but it can be forgotten to document here.

So Ducku corresponds lists in documentation as
- headers
- bullet points
- markdown code snippets

with potential lists in the project as
- files/folders in one folder
- JSON/YAML keys/values at the same level
- code specific:
  - module-level functions
  - module-level classes
  - class methods
  - function/method arguments
  - dictionary keys, values, and list elements
  - table-like data structures (uniform lists/arrays of objects)

*Terms here are for Python, but similar structures are supported for other languages as well.

### 4. Unused Module Detection (beta)

This use case helps you to identify modules which are not imported from anywhere. 
That means one of:
- This module is an entry point (e.g CLI script or Docker endpoint)
- This module is obsolete

In the first case it should be documented, since it's direct instructions of using the system
In the second case likely deleted.

--------------

For all the usecases are following programming languages are supported:

- Python
- JavaScript
- TypeScript
- Java
- Go
- Ruby

## 📦 Installation

### Install from PyPI (Recommended)

```bash
pip install ducku
```

Then `ducku` binary will be available globally

### Using in CI/CD

Example of usage in CI/CD (GitLab):

```yaml
documentation_check:
    image: yarax/ducku:latest
    stage: quality
    variables:
        PROJECT_PATH: "$CI_PROJECT_DIR"
    script:
        - ducku
```

Example for GitHub Actions:

```yaml
- name: Documentation Quality Check
  run: |
    docker run --rm \
      -v ${{ github.workspace }}:/workspace \
      -e PROJECT_PATH=/workspace \
      yarax/ducku:latest
```

Also feel free to utilize [`Dockerfile`](Dockerfile) to build and use your own image.

## 🚀 Usage

### Command Line Interface

#### Analyze a Single Project

Interactive mode (prompts for path):

```bash
ducku
```

Using `--target` flag to specify project path:

```bash
ducku --target /path/to/your/project
# or short form
ducku -t /path/to/your/project
```

Using `PROJECT_PATH` environment variable:

```bash
PROJECT_PATH=/path/to/your/project ducku
```

**Note:** The `--target` flag takes precedence over the `PROJECT_PATH` environment variable.

#### Analyze Multiple Projects
```bash
MULTI_FOLDER=/path/to/projects/directory ducku
```

#### Check Version
```bash
ducku --version
# or
ducku -v
```

#### Output Formats

Ducku supports multiple output formats for different use cases:

**Text format (default)** - Human-readable with colors and emojis:
```bash
ducku
# or explicitly
ducku --format text
```

**JSON format** - Machine-readable structured output:
```bash
ducku --format json
# or short form
ducku -f json
```

**HTML format** - HTML with headers and lists:
```bash
ducku --format html
```

## ⚙️ Configuration

Create a `.ducku.yaml` file in your project root:

```yaml
# Disable specific use cases
disabled_use_cases:
# possible values
  - unused_modules
  - pattern_search
  - partial_lists
  - spellcheck

# Additional documentation paths
documentation_paths:
  - /tmp/other_docs

# Paths to exclude from code analysis
code_paths_to_ignore:
  - vendor/
  - node_modules/

# This paths won't be collected as documentation
documentation_paths_to_ignore:
 - path/to/docs_to_ignore
# usecase specific options
use_case_options:
  unused_modules:
    enabled: false
  #...
  pattern_search:
    # Custom file patterns to skip
    disabled_patterns:
    # possible values
      - "Unix path"
      - "Windows path"
      - "Filename"
      - "Port Number"
      - "Environment variable"
      - "HTTP Routes"
  # If true quits with code 1 after printing all the reports. Default: false
fail_on_issues: false
```

## ✅ Pre-commit Hook

You can integrate Ducku into your Git workflow using pre-commit hooks to automatically check documentation quality before commits.

1. **Install pre-commit**:
```bash
pip install pre-commit
```

2. **Create `.pre-commit-config.yaml`** in your repository root:
```yaml
repos:
  - repo: local
    hooks:
      - id: ducku
        name: Documentation Quality Check
        entry: ducku
        language: system
        pass_filenames: false
        always_run: true
        env:
          - PROJECT_PATH=.
```

3. **Install the hook**:
```bash
pre-commit install
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`uv run pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Adding New Use Cases

To add a new analysis use case:

1. Create a new class inheriting from `BaseUseCase`
2. Implement the `report()` method
3. Add the use case to `bin/cli.py`
4. Write comprehensive tests

## 📝 License

This project is licensed under the Ducku Source Available License (DSAL) - see the [LICENSE](LICENSE) file for details.

**Key License Points:**
- ✅ Free for personal use, internal business use, and non-commercial purposes
- ✅ Educational and research use permitted
- ❌ Commercial documentation tools and services cannot use this software
- ❌ Cannot be integrated into paid documentation platforms
- 📖 Source code must remain available under the same license terms

For detailed terms and conditions, please review the full [LICENSE](LICENSE) file.