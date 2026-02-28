import json
from pathlib import Path
from typing import List
import yaml
from src.helpers.logger import get_logger
log = get_logger(__name__)

class IgnoreUnknownTagsLoader(yaml.SafeLoader):
    """
    Custom loader that ignores unknown YAML tags instead of throwing an error.
    """

def unknown_tag_handler(loader, tag_suffix, node):
    return 'unknownyamltag'

IgnoreUnknownTagsLoader.add_multi_constructor('', unknown_tag_handler)

def is_corrupted(value):
    # Convert to string if not already a string
    if not isinstance(value, str):
        value = str(value)
    return "\n" in value or len(value) > 50

def to_filter_key(key):
    filter_keys = {
        # Generic metadata
        "if", "when", "id", "uuid", "name", "type", "version", "lang", "language",
        "title", "description", "date", "created_at", "updated_at", "enabled", "disabled",
        "default", "value", "values", "key", "keys", "label", "labels", "tag", "tags",
        "metadata", "annotations", "properties", "options", "config", "configuration",
        "settings", "enabled", "disabled", "required", "optional",

        # Docker Compose service-level keys (appear under services::<name>)
        "image", "build", "restart", "container_name", "ports", "volumes", "environment",
        "env_file", "healthcheck", "depends_on", "networks", "command", "entrypoint",
        "working_dir", "user", "expose", "links", "logging", "deploy", "devices", "dns",
        "tmpfs", "cap_add", "cap_drop", "security_opt", "stdin_open", "tty", "profiles",
        "pull_policy", "platform", "secrets", "configs", "extends", "extra_hosts",
        "network_mode", "pid", "ipc", "shm_size", "sysctls", "ulimits", "mem_limit",
        "cpus", "privileged", "read_only",

        # Kubernetes manifest structural keys
        "apiversion", "kind", "spec", "status", "selector", "template", "containers",
        "replicas", "resources", "limits", "requests", "volumemounts", "envfrom",
        "livenessprobe", "readinessprobe", "startupprobe", "imagepullpolicy",
        "restartpolicy", "serviceaccountname", "nodeselector", "tolerations",
        "affinity", "initcontainers", "finalizers", "ownerreferences", "namespace",
        "generatename", "resourceversion", "uid", "creationtimestamp",

        # GitHub Actions / CI workflow structural keys
        "on", "jobs", "steps", "uses", "with", "run", "needs", "outputs",
        "permissions", "concurrency", "strategy", "matrix", "runs-on",
        "continue-on-error", "timeout-minutes", "fail-fast", "max-parallel",
        "before_script", "after_script", "artifacts", "cache", "stage", "rules",
        "workflow_dispatch", "push", "pull_request",

        # package.json structural keys
        "scripts", "dependencies", "devdependencies", "peerdependencies",
        "optionaldependencies", "engines", "files", "exports", "main", "module",
        "browser", "bin", "repository", "bugs", "homepage", "keywords", "license",
        "author", "contributors", "private", "workspaces", "resolutions", "overrides",
        "funding", "man", "directories",

        # Ansible playbook structural keys
        "hosts", "become", "gather_facts", "vars", "tasks", "handlers", "roles",
        "pre_tasks", "post_tasks", "notify", "register", "loop", "block", "rescue",
        "always", "ignore_errors", "delegate_to", "run_once", "changed_when",
        "failed_when", "with_items", "with_dict", "import_tasks", "include_tasks",

        # Terraform block type keywords
        "resource", "provider", "variable", "output", "module", "locals",
        "terraform", "required_providers", "backend",

        # OpenAPI / JSON Schema structural keys
        "openapi", "info", "paths", "components", "schemas", "responses",
        "parameters", "requestbody", "headers", "examples", "links", "callbacks",
        "security", "servers", "allof", "anyof", "oneof", "not", "items",
        "definitions", "additionalproperties", "patternproperties",
        "format", "minimum", "maximum", "minlength", "maxlength", "pattern",
        "enum", "nullable", "discriminator", "xml", "externalDocs",
    }
    if not isinstance(key, str):
        key = str(key)
    return key.lower() in filter_keys or len(key) > 30

def collect_key_values(data, parallel_entities, parent):
    from src.core.entity import Entity, EntitiesContainer  # Import here to avoid circular dependency
    key_items = EntitiesContainer(parent, "json_keys")
    value_items = EntitiesContainer(parent, "json_values")
    if isinstance(data, dict):
        for key, value in data.items():
            if not is_corrupted(key) and not to_filter_key(key):
                key_items.append(Entity(str(key)))
            if isinstance(value, (str, int, float, bool)):
                if not is_corrupted(value):
                    value_items.append(Entity(str(value)))
            else:
                collect_key_values(value, parallel_entities, parent + "::" + str(key))
        if key_items.entities:
            parallel_entities.append(key_items)
        if value_items.entities:
            parallel_entities.append(value_items)
    elif isinstance(data, list):
        for value in data:
            if isinstance(value, (str, int, float, bool)):
                if not is_corrupted(value):
                    value_items.append(Entity(str(value)))
            else:
                collect_key_values(value, parallel_entities, parent)
        if value_items.entities:
            parallel_entities.append(value_items)

def collect_json_keys(file: Path, parallel_entities: List):
    ext = file.suffix
    data = None
    if ext in (".yaml", ".yml"):
        try:
            content = file.read_text()
            data = yaml.load(content, Loader=IgnoreUnknownTagsLoader)
        except Exception as e:
            log.error(e)
    elif ext == ".json":
        content = file.read_text()
        try:
            data = json.loads(content)
        except Exception as e:
            log.error(e)
    if data:
        collect_key_values(data, parallel_entities, str(file))
