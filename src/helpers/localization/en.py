"""English word lists."""

GENERIC_TOKENS = {
    "user", "users", "profile", "settings", "config", "data", "list",
    "item", "items", "get", "set", "create", "update", "delete", "add",
    "remove", "default", "script", "name", "type"
}

CONTENT_CHECK_KEYWORDS = {
    "ci_cd": [
        "ci/cd", "pipeline", "continuous integration", "continuous deployment",
        "github actions", "gitlab ci", "jenkins", "circleci", "travis", "workflow",
    ],
    "docker": [
        "docker", "container", "dockerfile", "docker-compose", "image",
    ],
    "kubernetes": [
        "kubernetes", "k8s", "deployment", "pod", "service", "ingress", "kubectl",
    ],
    "serverless": [
        "serverless", "lambda", "function", "sam", "cloudformation",
    ],
    "terraform": [
        "terraform", "infrastructure", "iac", "tf",
    ],
    "makefile": [
        "make", "makefile", "build", "compile", "gmake", "build system",
    ],
    "precommit": [
        "pre-commit", "precommit", "git hook", "commit hook", "pre commit",
    ],
    "renovate": [
        "renovate", "dependency update", "automated update", "renovate bot",
    ],
    "dependabot": [
        "dependabot", "dependency update", "automated update", "github bot",
    ],
    "helm": [
        "helm", "helm chart", "kubernetes package", "chart", "helm install",
    ],
    "ansible": [
        "ansible", "playbook", "automation", "configuration management", "ansible-playbook",
    ],
    "vagrant": [
        "vagrant", "virtual machine", "vm", "vagrantfile", "vagrant up",
    ],
    "tox": [
        "tox", "test automation", "virtualenv", "testing", "tox environments",
    ],
    "nx": [
        "nx", "monorepo", "nx workspace", "nx build", "nrwl",
    ],
}

MOCK_FILENAME_PATTERNS = [
    "hello", "my_", "path_to", "xxx", "yyy", "zzz",
    "log_", "log.", "logs.", "myfile", "yourfile",
]

MOCK_DIR_PATTERNS = [
    "/some-dir/", "/some_dir/", "/somedir/",
]

MOCK_PATH_PATTERNS = [
    "/example.py", "/example.js", "/example.ts",
    "/sample.py", "/sample.js", "/sample.ts",
]
