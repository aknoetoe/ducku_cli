"""Content check use case for validating deployment artifacts in documentation."""

from pathlib import Path
from typing import Dict, List, Set
import re

from src.core.project import Project
from src.core.base_usecase import BaseUseCase
from src.core.report import Report, IssueType


class ContentCheck(BaseUseCase):
    """Base class for content validation checks.

    This use case validates that deployment artifacts referenced in documentation
    actually exist in the repository and are properly documented.
    """

    def __init__(self, project: Project):
        super().__init__(project)
        self.name = "content_check"
        self.sub_checks = [
            DeploymentArtifactsCheck(project)
        ]

    def report(self) -> str:
        """Generate a report by running all sub-checks."""
        result = Report()

        for sub_check in self.sub_checks:
            sub_report = sub_check.report()
            # Merge issues from sub-reports
            result.issues.extend(sub_report.issues)

        return str(result)


class DeploymentArtifactsCheck:
    """Check for deployment artifacts and verify they are documented.

    This sub-check looks for:
    - CI/CD configuration files (.gitlab-ci.yml, .github/workflows/*, etc.)
    - Dockerfiles and docker-compose files
    - Kubernetes manifests
    - Cloud deployment configs (serverless.yml, etc.)
    - Build automation (Makefile, etc.)
    - Dependency management (Renovate, Dependabot)
    - Git hooks (pre-commit)
    - Container orchestration (Helm, Kubernetes)
    - Configuration management (Ansible, Vagrant)
    - Test automation (Tox)
    - Monorepo tools (Nx)

    For each artifact found, it searches for relevant keywords in the documentation.
    If not found, it reports an issue.
    """

    # Common deployment artifact patterns
    DEPLOYMENT_ARTIFACTS = {
        'ci_cd': {
            'patterns': [
                '.gitlab-ci.yml',
                '.github/workflows/*.yml',
                '.github/workflows/*.yaml',
                'Jenkinsfile',
                '.circleci/config.yml',
                '.travis.yml',
                'azure-pipelines.yml',
                'bitbucket-pipelines.yml',
                '.drone.yml',
            ],
            'keywords': ['ci/cd', 'pipeline', 'continuous integration', 'continuous deployment',
                        'github actions', 'gitlab ci', 'jenkins', 'circleci', 'travis', 'workflow']
        },
        'docker': {
            'patterns': [
                'Dockerfile',
                'Dockerfile.*',
                'docker-compose.yml',
                'docker-compose.yaml',
                'docker-compose.*.yml',
                'docker-compose.*.yaml',
                '.dockerignore',
            ],
            'keywords': ['docker', 'container', 'dockerfile', 'docker-compose', 'image']
        },
        'kubernetes': {
            'patterns': [
                'k8s/*.yml',
                'k8s/*.yaml',
                'kubernetes/*.yml',
                'kubernetes/*.yaml',
                'deployment.yml',
                'deployment.yaml',
                'service.yml',
                'service.yaml',
                'ingress.yml',
                'ingress.yaml',
            ],
            'keywords': ['kubernetes', 'k8s', 'deployment', 'pod', 'service', 'ingress', 'kubectl']
        },
        'serverless': {
            'patterns': [
                'serverless.yml',
                'serverless.yaml',
                'serverless.*.yml',
                'sam.yml',
                'sam.yaml',
                'template.yml',
                'template.yaml',
            ],
            'keywords': ['serverless', 'lambda', 'function', 'sam', 'cloudformation']
        },
        'terraform': {
            'patterns': [
                '*.tf',
                'terraform/*.tf',
                '*.tfvars',
            ],
            'keywords': ['terraform', 'infrastructure', 'iac', 'tf']
        },
        'makefile': {
            'patterns': [
                'Makefile',
                'makefile',
                '*.mk',
                'GNUmakefile',
            ],
            'keywords': ['make', 'makefile', 'build', 'compile', 'gmake', 'build system']
        },
        'precommit': {
            'patterns': [
                '.pre-commit-config.yaml',
                '.pre-commit-config.yml',
            ],
            'keywords': ['pre-commit', 'precommit', 'git hook', 'commit hook', 'pre commit']
        },
        'renovate': {
            'patterns': [
                'renovate.json',
                '.renovaterc',
                '.renovaterc.json',
                '.renovaterc.json5',
                '.github/renovate.json',
                '.gitlab/renovate.json',
            ],
            'keywords': ['renovate', 'dependency update', 'automated update', 'renovate bot']
        },
        'dependabot': {
            'patterns': [
                '.github/dependabot.yml',
                '.github/dependabot.yaml',
            ],
            'keywords': ['dependabot', 'dependency update', 'automated update', 'github bot']
        },
        'helm': {
            'patterns': [
                'Chart.yaml',
                'Chart.yml',
                'values.yaml',
                'values.yml',
                'charts/*/Chart.yaml',
                'helm/*/Chart.yaml',
            ],
            'keywords': ['helm', 'helm chart', 'kubernetes package', 'chart', 'helm install']
        },
        'ansible': {
            'patterns': [
                'ansible.cfg',
                'playbook.yml',
                'playbook.yaml',
                'site.yml',
                'site.yaml',
                'ansible/*.yml',
                'ansible/*.yaml',
                'inventory.ini',
                'inventory.yml',
                'inventory.yaml',
            ],
            'keywords': ['ansible', 'playbook', 'automation', 'configuration management', 'ansible-playbook']
        },
        'vagrant': {
            'patterns': [
                'Vagrantfile',
            ],
            'keywords': ['vagrant', 'virtual machine', 'vm', 'vagrantfile', 'vagrant up']
        },
        'tox': {
            'patterns': [
                'tox.ini',
            ],
            'keywords': ['tox', 'test automation', 'virtualenv', 'testing', 'tox environments']
        },
        'nx': {
            'patterns': [
                'nx.json',
                'workspace.json',
            ],
            'keywords': ['nx', 'monorepo', 'nx workspace', 'nx build', 'nrwl']
        },
    }

    def __init__(self, project: Project):
        self.project = project

    def report(self) -> Report:
        """Check deployment artifacts and report missing documentation."""
        result = Report()

        # Find all deployment artifacts in the project
        found_artifacts = self._find_deployment_artifacts()

        if not found_artifacts:
            # No deployment artifacts found - this is not necessarily an issue
            return result

        # Get all documentation content
        doc_content = self._get_documentation_content()

        # Check each artifact type
        for artifact_type, artifacts in found_artifacts.items():
            if not artifacts:
                continue

            keywords = self.DEPLOYMENT_ARTIFACTS[artifact_type]['keywords']

            # Check if any of the keywords appear in documentation
            found_keyword = False
            for keyword in keywords:
                # Case-insensitive search for keywords
                if re.search(r'\b' + re.escape(keyword) + r'\b', doc_content, re.IGNORECASE):
                    found_keyword = True
                    break

            if not found_keyword:
                # Report the issue
                # Ensure project_root is a Path object for relative_to
                if isinstance(self.project.project_root, Path):
                    project_root = self.project.project_root
                else:
                    project_root = Path(self.project.project_root)

                artifact_list = ', '.join(str(a.relative_to(project_root)) for a in artifacts[:3])
                if len(artifacts) > 3:
                    artifact_list += f' (and {len(artifacts) - 3} more)'

                result.add_issue(
                    f"Found {artifact_type.replace('_', ' ')} artifacts ({artifact_list}) but no related keywords "
                    f"found in documentation. Consider documenting: {', '.join(keywords[:3])}",
                    level=IssueType.WARNING,
                    artifact_type=artifact_type,
                    artifacts=[str(a) for a in artifacts],
                    missing_keywords=keywords
                )

        return result

    def _find_deployment_artifacts(self) -> Dict[str, List[Path]]:
        """Find deployment artifacts in the project."""
        found = {key: [] for key in self.DEPLOYMENT_ARTIFACTS.keys()}

        # Ensure project_root is a Path object
        if isinstance(self.project.project_root, Path):
            project_root = self.project.project_root
        else:
            project_root = Path(self.project.project_root)

        for artifact_type, config in self.DEPLOYMENT_ARTIFACTS.items():
            patterns = config['patterns']

            for pattern in patterns:
                # Handle glob patterns
                if '*' in pattern:
                    matching_files = list(project_root.glob(pattern))
                    found[artifact_type].extend(matching_files)
                else:
                    # Exact match
                    file_path = project_root / pattern
                    if file_path.exists():
                        found[artifact_type].append(file_path)

        return found

    def _get_documentation_content(self) -> str:
        """Get all documentation content as a single string."""
        content_parts = []

        for doc_part in self.project.documentation.doc_parts:
            if doc_part.source.type == "file" and "path" in doc_part.source.metadata:
                file_path = Path(doc_part.source.metadata["path"])
                if file_path.exists():
                    try:
                        content_parts.append(file_path.read_text(encoding='utf-8', errors='ignore'))
                    except Exception:
                        # Skip files that can't be read
                        pass

        return '\n'.join(content_parts)
