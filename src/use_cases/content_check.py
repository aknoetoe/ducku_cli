"""Content check use case for validating deployment artifacts in documentation."""

from pathlib import Path
from typing import Dict, List, Set
import re

from src.core.project import Project
from src.core.base_usecase import BaseUseCase
from src.core.report import Report, IssueType
from src.helpers.localization import get_content_keywords


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

    def report(self) -> Report:
        """Generate a report by running all sub-checks."""
        result = Report()

        for sub_check in self.sub_checks:
            sub_report = sub_check.report()
            # Merge issues from sub-reports
            result.issues.extend(sub_report.issues)

        return result


class DeploymentArtifactsCheck:
    """Check for deployment artifacts and verify they are documented.

    For each artifact found, it searches for relevant keywords in the documentation.
    If not found, it reports an issue.
    """

    # Common deployment artifact patterns (keywords come from localization)
    DEPLOYMENT_ARTIFACTS = {
        'ci_cd': [
            '.gitlab-ci.yml', '.github/workflows/*.yml', '.github/workflows/*.yaml',
            'Jenkinsfile', '.circleci/config.yml', '.travis.yml',
            'azure-pipelines.yml', 'bitbucket-pipelines.yml', '.drone.yml',
        ],
        'docker': [
            'Dockerfile', 'Dockerfile.*',
            'docker-compose.yml', 'docker-compose.yaml',
            'docker-compose.*.yml', 'docker-compose.*.yaml', '.dockerignore',
        ],
        'kubernetes': [
            'k8s/*.yml', 'k8s/*.yaml', 'kubernetes/*.yml', 'kubernetes/*.yaml',
            'deployment.yml', 'deployment.yaml', 'service.yml', 'service.yaml',
            'ingress.yml', 'ingress.yaml',
        ],
        'serverless': [
            'serverless.yml', 'serverless.yaml', 'serverless.*.yml',
            'sam.yml', 'sam.yaml', 'template.yml', 'template.yaml',
        ],
        'terraform': ['*.tf', 'terraform/*.tf', '*.tfvars'],
        'makefile': ['Makefile', 'makefile', '*.mk', 'GNUmakefile'],
        'precommit': ['.pre-commit-config.yaml', '.pre-commit-config.yml'],
        'renovate': [
            'renovate.json', '.renovaterc', '.renovaterc.json', '.renovaterc.json5',
            '.github/renovate.json', '.gitlab/renovate.json',
        ],
        'dependabot': ['.github/dependabot.yml', '.github/dependabot.yaml'],
        'helm': [
            'Chart.yaml', 'Chart.yml', 'values.yaml', 'values.yml',
            'charts/*/Chart.yaml', 'helm/*/Chart.yaml',
        ],
        'ansible': [
            'ansible.cfg', 'playbook.yml', 'playbook.yaml', 'site.yml', 'site.yaml',
            'ansible/*.yml', 'ansible/*.yaml', 'inventory.ini', 'inventory.yml', 'inventory.yaml',
        ],
        'vagrant': ['Vagrantfile'],
        'tox': ['tox.ini'],
        'nx': ['nx.json', 'workspace.json'],
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
        doc_content = self.project.documentation.content

        # Check each artifact type
        for artifact_type, artifacts in found_artifacts.items():
            if not artifacts:
                continue

            keywords = get_content_keywords(artifact_type)
            if not keywords:
                continue

            # Check if any of the keywords appear in documentation
            found_keyword = False
            for keyword in keywords:
                # Case-insensitive search for keywords
                if re.search(r'\b' + re.escape(keyword) + r'\b', doc_content, re.IGNORECASE):
                    found_keyword = True
                    break

            if not found_keyword:
                # Report the issue
                artifact_list = ', '.join(str(a.relative_to(self.project.project_root)) for a in artifacts[:3])
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

        for artifact_type, patterns in self.DEPLOYMENT_ARTIFACTS.items():
            for pattern in patterns:
                # Handle glob patterns
                if '*' in pattern:
                    matching_files = list(self.project.project_root.glob(pattern))
                    found[artifact_type].extend(matching_files)
                else:
                    # Exact match
                    file_path = self.project.project_root / pattern
                    if file_path.exists():
                        found[artifact_type].append(file_path)

        return found
