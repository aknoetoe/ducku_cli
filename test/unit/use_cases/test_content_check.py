"""Tests for the ContentCheck use case."""

from pathlib import Path
import tempfile
import shutil
from src.use_cases.content_check import ContentCheck, DeploymentArtifactsCheck
from src.core.project import Project


def test_deployment_artifacts_found_and_documented():
    """Test that deployment artifacts are found and documented properly."""
    # Create a temporary project directory
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create a Dockerfile
        dockerfile = project_root / "Dockerfile"
        dockerfile.write_text("FROM python:3.10\nRUN pip install ducku\n")

        # Create README with Docker documentation
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

This project uses Docker for containerization.

## Building the Docker Image

```bash
docker build -t myapp .
```
""")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should not report issues because Docker is documented
        assert report == "", f"Expected no issues but got: {report}"


def test_deployment_artifacts_found_but_not_documented():
    """Test that missing documentation is reported for deployment artifacts."""
    # Create a temporary project directory
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create a Dockerfile but no documentation
        dockerfile = project_root / "Dockerfile"
        dockerfile.write_text("FROM python:3.10\nRUN pip install ducku\n")

        # Create README without Docker documentation
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

This is a test project with no deployment documentation.
""")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should report issues because Docker is not documented
        assert report != "", "Expected issues for undocumented Docker artifact"
        assert "docker" in report.lower()


def test_ci_cd_artifacts_detection():
    """Test detection of CI/CD configuration files."""
    # Create a temporary project directory
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create GitHub Actions workflow
        workflows_dir = project_root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True)
        workflow_file = workflows_dir / "ci.yml"
        workflow_file.write_text("""
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
""")

        # Create README without CI/CD documentation
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

This is a test project.
""")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should report issues because CI/CD is not documented
        assert report != "", "Expected issues for undocumented CI/CD artifact"
        assert "ci" in report.lower() or "workflow" in report.lower()


def test_multiple_artifact_types():
    """Test detection of multiple deployment artifact types."""
    # Create a temporary project directory
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create multiple deployment artifacts
        dockerfile = project_root / "Dockerfile"
        dockerfile.write_text("FROM python:3.10\n")

        docker_compose = project_root / "docker-compose.yml"
        docker_compose.write_text("""
version: '3'
services:
  app:
    build: .
""")

        gitlab_ci = project_root / ".gitlab-ci.yml"
        gitlab_ci.write_text("""
stages:
  - test
test:
  script:
    - pytest
""")

        # Create README with partial documentation (only Docker)
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

This project uses Docker containers.
""")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should report issues for undocumented CI/CD
        assert report != "", "Expected issues for undocumented CI/CD"
        report_lower = report.lower()

        # Docker should be documented, so no warning for it
        # But CI/CD should not be documented
        assert "ci" in report_lower or "gitlab" in report_lower or "pipeline" in report_lower


def test_no_deployment_artifacts():
    """Test that no issues are reported when there are no deployment artifacts."""
    # Create a temporary project directory
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create only a README with no deployment artifacts
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

This is a simple test project with no deployment configuration.
""")

        # Create a simple Python file
        py_file = project_root / "main.py"
        py_file.write_text("print('Hello, world!')\n")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should not report any issues
        assert report == "", f"Expected no issues but got: {report}"


def test_deployment_artifacts_check_directly():
    """Test the DeploymentArtifactsCheck class directly."""
    # Create a temporary project directory
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create Kubernetes manifests
        k8s_dir = project_root / "k8s"
        k8s_dir.mkdir()
        deployment = k8s_dir / "deployment.yml"
        deployment.write_text("""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
""")

        # Create README without k8s documentation
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

This is a test project.
""")

        # Create project and run check
        project = Project(project_root)
        checker = DeploymentArtifactsCheck(project)
        report = checker.report()

        # Should report issues for undocumented Kubernetes
        assert report.has_issues(), "Expected issues for undocumented Kubernetes"
        report_str = str(report).lower()
        assert "kubernetes" in report_str or "k8s" in report_str


def test_case_insensitive_keyword_matching():
    """Test that keyword matching is case-insensitive."""
    # Create a temporary project directory
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create a Dockerfile
        dockerfile = project_root / "Dockerfile"
        dockerfile.write_text("FROM python:3.10\n")

        # Create README with uppercase DOCKER
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

This project uses DOCKER for deployment.
""")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should not report issues because "DOCKER" matches "docker"
        assert report == "", f"Expected no issues but got: {report}"


def test_makefile_detection():
    """Test detection of Makefile."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create Makefile
        makefile = project_root / "Makefile"
        makefile.write_text("""
.PHONY: build test clean

build:
\tgcc -o myapp main.c

test:
\tpytest tests/

clean:
\trm -f myapp
""")

        # Create README without Makefile documentation
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

This is a test project.
""")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should report issues for undocumented Makefile
        assert report != "", "Expected issues for undocumented Makefile"
        assert "makefile" in report.lower() or "make" in report.lower()


def test_precommit_detection():
    """Test detection of pre-commit configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create pre-commit config
        precommit = project_root / ".pre-commit-config.yaml"
        precommit.write_text("""
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
""")

        # Create README without pre-commit documentation
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

This is a test project.
""")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should report issues for undocumented pre-commit
        assert report != "", "Expected issues for undocumented pre-commit"
        assert "pre-commit" in report.lower() or "precommit" in report.lower() or "hook" in report.lower()


def test_renovate_detection():
    """Test detection of Renovate configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create Renovate config
        renovate = project_root / "renovate.json"
        renovate.write_text("""
{
  "extends": ["config:base"],
  "packageRules": [
    {
      "updateTypes": ["minor", "patch"],
      "automerge": true
    }
  ]
}
""")

        # Create README without Renovate documentation
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

This is a test project.
""")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should report issues for undocumented Renovate
        assert report != "", "Expected issues for undocumented Renovate"
        assert "renovate" in report.lower()


def test_dependabot_detection():
    """Test detection of Dependabot configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create Dependabot config
        github_dir = project_root / ".github"
        github_dir.mkdir()
        dependabot = github_dir / "dependabot.yml"
        dependabot.write_text("""
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
""")

        # Create README without Dependabot documentation
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

This is a test project.
""")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should report issues for undocumented Dependabot
        assert report != "", "Expected issues for undocumented Dependabot"
        assert "dependabot" in report.lower()


def test_helm_detection():
    """Test detection of Helm charts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create Helm Chart
        chart = project_root / "Chart.yaml"
        chart.write_text("""
apiVersion: v2
name: myapp
description: A Helm chart for myapp
type: application
version: 0.1.0
appVersion: "1.0"
""")

        values = project_root / "values.yaml"
        values.write_text("""
replicaCount: 1
image:
  repository: myapp
  tag: latest
""")

        # Create README without Helm documentation
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

This is a test project.
""")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should report issues for undocumented Helm
        assert report != "", "Expected issues for undocumented Helm"
        assert "helm" in report.lower() or "chart" in report.lower()


def test_ansible_detection():
    """Test detection of Ansible configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create Ansible config
        ansible_cfg = project_root / "ansible.cfg"
        ansible_cfg.write_text("""
[defaults]
inventory = inventory.ini
host_key_checking = False
""")

        playbook = project_root / "playbook.yml"
        playbook.write_text("""
---
- name: Configure web servers
  hosts: webservers
  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present
""")

        # Create README without Ansible documentation
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

This is a test project.
""")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should report issues for undocumented Ansible
        assert report != "", "Expected issues for undocumented Ansible"
        assert "ansible" in report.lower() or "playbook" in report.lower()


def test_vagrant_detection():
    """Test detection of Vagrantfile."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create Vagrantfile
        vagrantfile = project_root / "Vagrantfile"
        vagrantfile.write_text("""
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  config.vm.network "private_network", ip: "192.168.33.10"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "1024"
  end
end
""")

        # Create README without Vagrant documentation
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

This is a test project.
""")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should report issues for undocumented Vagrant
        assert report != "", "Expected issues for undocumented Vagrant"
        assert "vagrant" in report.lower()


def test_tox_detection():
    """Test detection of Tox configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create tox.ini
        tox_ini = project_root / "tox.ini"
        tox_ini.write_text("""
[tox]
envlist = py39,py310,py311

[testenv]
deps = pytest
commands = pytest tests/
""")

        # Create README without Tox documentation
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

This is a test project.
""")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should report issues for undocumented Tox
        assert report != "", "Expected issues for undocumented Tox"
        assert "tox" in report.lower()


def test_nx_detection():
    """Test detection of Nx workspace configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create nx.json
        nx_json = project_root / "nx.json"
        nx_json.write_text("""
{
  "npmScope": "myorg",
  "affected": {
    "defaultBase": "main"
  },
  "tasksRunnerOptions": {
    "default": {
      "runner": "nx/tasks-runners/default",
      "options": {
        "cacheableOperations": ["build", "test", "lint"]
      }
    }
  }
}
""")

        # Create README without Nx documentation
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

This is a test project.
""")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should report issues for undocumented Nx
        assert report != "", "Expected issues for undocumented Nx"
        assert "nx" in report.lower() or "monorepo" in report.lower()


def test_multiple_new_artifacts_comprehensive():
    """Test detection of multiple new artifact types with partial documentation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create Makefile
        makefile = project_root / "Makefile"
        makefile.write_text("build:\n\techo 'Building...'\n")

        # Create pre-commit config
        precommit = project_root / ".pre-commit-config.yaml"
        precommit.write_text("repos: []\n")

        # Create Helm chart
        chart = project_root / "Chart.yaml"
        chart.write_text("apiVersion: v2\nname: myapp\n")

        # Create tox.ini
        tox_ini = project_root / "tox.ini"
        tox_ini.write_text("[tox]\nenvlist = py39\n")

        # Create README with partial documentation (only mentions Makefile and Helm)
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

## Building

Use `make build` to build the project.

## Deployment

We use Helm charts for Kubernetes deployment.
""")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should report issues for undocumented artifacts (pre-commit and tox)
        assert report != "", "Expected issues for undocumented artifacts"
        report_lower = report.lower()

        # Makefile and Helm should NOT be reported (documented)
        # But pre-commit and tox should be reported (not documented)
        assert "precommit" in report_lower or "pre-commit" in report_lower or "hook" in report_lower
        assert "tox" in report_lower


def test_makefile_documented():
    """Test that documented Makefile does not raise issues."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create Makefile
        makefile = project_root / "Makefile"
        makefile.write_text("build:\n\techo 'Building...'\n")

        # Create README with Makefile documentation
        readme = project_root / "README.md"
        readme.write_text("""
# Test Project

## Building

This project uses a Makefile for build automation.
Run `make build` to compile the project.
""")

        # Create project and run check
        project = Project(project_root)
        use_case = ContentCheck(project)
        report = use_case.report()

        # Should not report issues because Makefile is documented
        assert report == "", f"Expected no issues but got: {report}"
