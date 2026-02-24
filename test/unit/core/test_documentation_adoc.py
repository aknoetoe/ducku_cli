from anytree import RenderTree
from src.core.documentation import DocPart, Documentation
from src.core.entity import collect_docs_entities


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _from_adoc(content: str) -> Documentation:
    return Documentation().from_string(content, "asciidoc")


# ---------------------------------------------------------------------------
# Format registry
# ---------------------------------------------------------------------------

def test_adoc_extensions_in_format_parsers():
    """Both .adoc and .asciidoc must be registered in the format parser registry."""
    assert ".adoc" in DocPart.FORMAT_PARSERS
    assert ".asciidoc" in DocPart.FORMAT_PARSERS
    assert "asciidoc" in DocPart.FORMAT_PARSERS
    assert DocPart.FORMAT_PARSERS[".adoc"] == "_parse_adoc"
    assert DocPart.FORMAT_PARSERS[".asciidoc"] == "_parse_adoc"


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def test_process_file_picks_up_adoc(tmp_path):
    """.adoc files are discovered and loaded by Documentation.process_file."""
    adoc_file = tmp_path / "guide.adoc"
    adoc_file.write_text("= Title\n\nSome content.\n")

    doc = Documentation()
    doc.process_file(adoc_file)

    assert len(doc.doc_parts) == 1


def test_process_file_picks_up_asciidoc(tmp_path):
    """.asciidoc files are discovered and loaded by Documentation.process_file."""
    adoc_file = tmp_path / "guide.asciidoc"
    adoc_file.write_text("= Title\n\nSome content.\n")

    doc = Documentation()
    doc.process_file(adoc_file)

    assert len(doc.doc_parts) == 1


def test_process_file_skips_unknown_extension(tmp_path):
    """Files with unregistered extensions are ignored."""
    txt_file = tmp_path / "guide.txt"
    txt_file.write_text("= Title\n")

    doc = Documentation()
    doc.process_file(txt_file)

    assert len(doc.doc_parts) == 0


def test_process_folder_discovers_adoc_files(tmp_path):
    """process_folder recursively picks up .adoc files."""
    sub = tmp_path / "docs"
    sub.mkdir()
    (sub / "a.adoc").write_text("= A\n\nContent.\n")
    (sub / "b.adoc").write_text("= B\n\nContent.\n")
    (sub / "ignored.txt").write_text("not adoc\n")

    doc = Documentation()
    doc.process_folder(tmp_path)

    assert len(doc.doc_parts) == 2


# ---------------------------------------------------------------------------
# Heading parsing
# ---------------------------------------------------------------------------

ADOC_HEADINGS = """\
= Main Title

Introduction.

== Installation

=== Prerequisites

Some text.

=== Steps

More text.

== Configuration

=== Environment Variables

Details here.
"""


def test_parse_adoc_headers_root_children():
    doc = _from_adoc(ADOC_HEADINGS).doc_parts[0]
    assert len(doc.headers.children) == 1
    assert doc.headers.children[0].name == "Main Title"
    assert doc.headers.children[0].level == 1


def test_parse_adoc_headers_second_level():
    doc = _from_adoc(ADOC_HEADINGS).doc_parts[0]
    h1 = doc.headers.children[0]
    child_names = [c.name for c in h1.children]
    assert "Installation" in child_names
    assert "Configuration" in child_names


def test_parse_adoc_headers_third_level():
    doc = _from_adoc(ADOC_HEADINGS).doc_parts[0]
    h1 = doc.headers.children[0]
    installation = next(c for c in h1.children if c.name == "Installation")
    third_level_names = [c.name for c in installation.children]
    assert "Prerequisites" in third_level_names
    assert "Steps" in third_level_names


def test_parse_adoc_headers_level_attribute():
    doc = _from_adoc(ADOC_HEADINGS).doc_parts[0]
    h1 = doc.headers.children[0]
    h2 = next(c for c in h1.children if c.name == "Installation")
    h3 = next(c for c in h2.children if c.name == "Prerequisites")
    assert h2.level == 2
    assert h3.level == 3


# ---------------------------------------------------------------------------
# List parsing
# ---------------------------------------------------------------------------

ADOC_LISTS = """\
= Doc

== Setup

=== Bullet section

* Alpha
* Beta
** Beta nested
* Gamma

=== Ordered section

. First step
. Second step
.. Sub step A
.. Sub step B
. Third step
"""


def test_parse_adoc_bullet_list_items():
    doc = _from_adoc(ADOC_LISTS).doc_parts[0]

    all_items = []
    for _, _, node in RenderTree(doc.lists):
        if node.kind == "list_item":
            all_items.append(node.name)

    assert "Alpha" in all_items
    assert "Beta" in all_items
    assert "Gamma" in all_items


def test_parse_adoc_ordered_list_items():
    doc = _from_adoc(ADOC_LISTS).doc_parts[0]

    all_items = []
    for _, _, node in RenderTree(doc.lists):
        if node.kind == "list_item":
            all_items.append(node.name)

    assert "First step" in all_items
    assert "Second step" in all_items
    assert "Third step" in all_items


def test_parse_adoc_nested_bullet_list():
    doc = _from_adoc(ADOC_LISTS).doc_parts[0]

    nested = []
    for _, _, node in RenderTree(doc.lists):
        if node.kind == "list_item" and node.name == "Beta nested":
            nested.append(node)

    assert len(nested) == 1, "Nested bullet item 'Beta nested' should be present"


def test_parse_adoc_nested_ordered_list():
    doc = _from_adoc(ADOC_LISTS).doc_parts[0]

    sub_items = []
    for _, _, node in RenderTree(doc.lists):
        if node.kind == "list_item" and node.name in ("Sub step A", "Sub step B"):
            sub_items.append(node.name)

    assert "Sub step A" in sub_items
    assert "Sub step B" in sub_items


def test_parse_adoc_list_header_context():
    """Lists are placed under the correct header node in the lists tree."""
    doc = _from_adoc(ADOC_LISTS).doc_parts[0]

    # The lists tree should have header nodes reflecting the header hierarchy
    all_nodes = [node for _, _, node in RenderTree(doc.lists)]
    node_names = [n.name for n in all_nodes]
    assert "Bullet section" in node_names
    assert "Ordered section" in node_names


# ---------------------------------------------------------------------------
# Code-block parsing
# ---------------------------------------------------------------------------

ADOC_CODE_BLOCKS = """\
= Configuration Guide

== Database

[source,yaml]
----
database:
  host: localhost
  port: 5432
  dbname: mydb
----

=== Cache

[source,yaml]
----
cache:
  ttl: 300
  backend: redis
----

== API

[source,json]
----
{
  "api_key": "abc123",
  "timeout": 30
}
----
"""


def test_parse_adoc_code_blocks_count():
    doc = _from_adoc(ADOC_CODE_BLOCKS).doc_parts[0]
    assert len(doc.code_blocks) == 3


def test_parse_adoc_code_block_language():
    doc = _from_adoc(ADOC_CODE_BLOCKS).doc_parts[0]
    languages = [cb["language"] for cb in doc.code_blocks]
    assert languages.count("yaml") == 2
    assert languages.count("json") == 1


def test_parse_adoc_code_block_content():
    doc = _from_adoc(ADOC_CODE_BLOCKS).doc_parts[0]
    yaml_blocks = [cb for cb in doc.code_blocks if cb["language"] == "yaml"]
    all_content = "\n".join(cb["content"] for cb in yaml_blocks)
    assert "localhost" in all_content
    assert "5432" in all_content
    assert "redis" in all_content


def test_parse_adoc_code_block_header_context():
    """Code blocks carry the full header hierarchy in their parent_path."""
    doc = _from_adoc(ADOC_CODE_BLOCKS).doc_parts[0]

    parents = [cb["parent_path"] for cb in doc.code_blocks]

    db_blocks = [p for p in parents if "::h2::Database" in p]
    api_blocks = [p for p in parents if "::h2::API" in p]
    cache_blocks = [p for p in parents if "::h3::Cache" in p]

    assert len(db_blocks) >= 1, f"Expected Database header in path, got: {parents}"
    assert len(api_blocks) >= 1, f"Expected API header in path, got: {parents}"
    assert len(cache_blocks) >= 1, f"Expected Cache header in path, got: {parents}"


def test_parse_adoc_code_block_full_header_path():
    """The parent_path for a deeply nested code block includes all ancestor headers."""
    doc = _from_adoc(ADOC_CODE_BLOCKS).doc_parts[0]

    cache_block = next(
        cb for cb in doc.code_blocks
        if "::h3::Cache" in cb["parent_path"]
    )
    assert "::h1::Configuration Guide" in cache_block["parent_path"]
    assert "::h2::Database" in cache_block["parent_path"]
    assert "::h3::Cache" in cache_block["parent_path"]


# ---------------------------------------------------------------------------
# Entity extraction
# ---------------------------------------------------------------------------

def test_adoc_entities_headers():
    """collect_docs_entities extracts header-based entities from adoc content."""
    content = """\
= API Reference

== Authentication

=== OAuth2

Details.

=== API Keys

Details.

== Endpoints

=== Users

Details.
"""
    doc = Documentation().from_string(content, "asciidoc")
    entities = collect_docs_entities(doc)

    auth_container = next(
        (c for c in entities if "::h2::Authentication" in c.parent and "::h3::" not in c.parent),
        None,
    )
    assert auth_container is not None, "Should have container for Authentication"
    entity_names = [e.content for e in auth_container.entities]
    assert "OAuth2" in entity_names
    assert "API Keys" in entity_names


def test_adoc_entities_yaml_code_block():
    """collect_docs_entities extracts YAML keys/values from adoc code blocks."""
    content = """\
= Config

[source,yaml]
----
server:
  host: 0.0.0.0
  port: 8080
----
"""
    doc = Documentation().from_string(content, "asciidoc")
    entities = collect_docs_entities(doc)

    code_containers = [c for c in entities if "code_block_yaml" in c.parent]
    assert len(code_containers) >= 1

    all_names = [e.content for c in code_containers for e in c.entities]
    assert "server" in all_names
    assert "host" in all_names
    assert "port" in all_names
    assert "0.0.0.0" in all_names
    assert "8080" in all_names


def test_adoc_entities_json_code_block():
    """collect_docs_entities extracts JSON keys/values from adoc code blocks."""
    content = """\
= Config

[source,json]
----
{
  "app_name": "MyApp",
  "timeout": 30
}
----
"""
    doc = Documentation().from_string(content, "asciidoc")
    entities = collect_docs_entities(doc)

    code_containers = [c for c in entities if "code_block_json" in c.parent]
    assert len(code_containers) >= 1

    all_names = [e.content for c in code_containers for e in c.entities]
    assert "app_name" in all_names
    assert "MyApp" in all_names
    assert "timeout" in all_names
    assert "30" in all_names


def test_adoc_docfile_uses_adoc_parser(tmp_path):
    """DocFile with a .adoc path routes through _parse_adoc, not _parse_md."""
    adoc_file = tmp_path / "readme.adoc"
    adoc_file.write_text("= My Project\n\n== Overview\n\nText.\n")

    doc = Documentation()
    doc.process_file(adoc_file)
    doc.process_content()

    part = doc.doc_parts[0]
    assert len(part.headers.children) == 1
    assert part.headers.children[0].name == "My Project"
