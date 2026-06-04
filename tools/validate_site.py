#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROOT_PREFIX = f"{ROOT.as_posix()}/"
ERRORS: list[str] = []
FRONT_MATTER_REQUIRED = ["title", "type", "status", "publishedAt", "updatedAt", "summary"]


def main() -> int:
    registry = read_json("data/registry.json")
    content = read_json("data/content.json")
    projects = [load_entry(entry) for entry in registry.get("projects", [])]
    article_entries = registry.get("methodArticles", registry.get("articles", []))
    articles = [load_entry(entry) for entry in article_entries]
    methods = registry.get("methods", [])

    ids = {
        "projects": {entry.get("id") for entry in projects},
        "articles": {entry.get("id") for entry in articles},
        "methods": {entry.get("id") for entry in methods},
    }

    for project in projects:
        validate_project(project, ids)
    for article in articles:
        validate_article(article, ids)
    validate_methods(methods, ids)
    validate_reading_paths(content, ids)
    validate_static_files()

    if ERRORS:
        print(f"Site validation failed with {len(ERRORS)} issue(s):", file=sys.stderr)
        for error in ERRORS:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Site validation passed: {len(projects)} projects, {len(articles)} articles, {len(methods)} methods.")
    return 0


def load_entry(entry: dict) -> dict:
    if not entry.get("data") and entry.get("content"):
        return dict(entry)
    data = read_json(entry.get("data", ""))
    if entry.get("id") != data.get("id"):
        ERRORS.append(f"{entry.get('data')}: registry id {entry.get('id')} does not match data id {data.get('id')}")
    return data


def validate_project(project: dict, ids: dict[str, set[str]]) -> None:
    label = f"project:{project.get('id')}"
    markdown_only = bool(project.get("content")) and not project.get("media") and not project.get("claim")
    if markdown_only:
        require_fields(project, label, ["id", "title", "content"])
        validate_markdown_content(project, label, ids)
        validate_related(project.get("related", {}), ids, label)
        return

    require_fields(project, label, ["id", "title", "summary", "metadata", "claim", "media", "reproducibility", "references", "related"])
    require_fields(project.get("metadata", {}), f"{label}.metadata", ["authors", "publishedAt", "updatedAt", "status", "tags", "readingMinutes"])
    require_fields(project.get("claim", {}), f"{label}.claim", ["question", "contribution", "findings", "limitations"])

    if not project.get("evidence"):
        ERRORS.append(f"{label}: evidence must contain at least one item")

    for item in project.get("media", {}).get("items", []):
        src = item.get("src")
        if not src:
            ERRORS.append(f"{label}: media item {item.get('title')} is missing src")
        else:
            ensure_exists(src, f"{label}: missing media asset")
        if not item.get("title"):
            ERRORS.append(f"{label}: media item {src} is missing title")
        if not item.get("sourceLabel") and not item.get("method"):
            ERRORS.append(f"{label}: media item {src} needs sourceLabel or method")

    if not project.get("reproducibility", {}).get("commands"):
        ERRORS.append(f"{label}: reproducibility.commands must contain at least one command")
    validate_markdown_content(project, label, ids)
    validate_related(project.get("related", {}), ids, label)


def validate_article(article: dict, ids: dict[str, set[str]]) -> None:
    label = f"article:{article.get('id')}"
    markdown_only = bool(article.get("content")) and not article.get("blocks") and not article.get("metadata")
    if markdown_only:
        require_fields(article, label, ["id", "title", "content"])
        validate_markdown_content(article, label, ids)
        validate_related(article.get("related", {}), ids, label)
        return

    require_fields(article, label, ["id", "title", "summary", "metadata", "references", "related"])
    require_fields(article.get("metadata", {}), f"{label}.metadata", ["authors", "publishedAt", "updatedAt", "status", "tags", "readingMinutes"])
    if not article.get("blocks") and not article.get("content"):
        ERRORS.append(f"{label}: provide either blocks or markdown content")
    validate_markdown_content(article, label, ids)
    validate_related(article.get("related", {}), ids, label)


def validate_markdown_content(entry: dict, label: str, ids: dict[str, set[str]]) -> None:
    content = entry.get("content")
    if not content:
        return
    ensure_exists(content, f"{label}: missing markdown content")
    path = site_file_path(content)
    if path is None:
        return
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    scan_text = strip_fenced_code(text)
    if not text.startswith("---"):
        ERRORS.append(f"{label}: markdown content should start with front matter")
        frontmatter = {}
    else:
        frontmatter = parse_frontmatter(text)
        for field in FRONT_MATTER_REQUIRED:
            if frontmatter.get(field) in (None, "", []):
                ERRORS.append(f"{label}: front matter missing {field}")
        validate_frontmatter_links(frontmatter, entry, label, ids)

    for image in re.findall(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]+\")?\)", scan_text):
        if image.startswith(("http://", "https://", "#")):
            continue
        ensure_exists(resolve_content_path(image, content), f"{label}: missing markdown image")
    for link in re.findall(r"(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+\"[^\"]+\")?\)", scan_text):
        validate_internal_link(link, f"{label}: missing markdown link target", content)
    validate_citations(scan_text, entry, label)
    validate_shortcodes(scan_text, entry, label)


def strip_fenced_code(text: str) -> str:
    without_blocks = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`]*`", "", without_blocks)


def parse_frontmatter(text: str) -> dict:
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    data: dict[str, object] = {}
    active_key: str | None = None
    for raw_line in text[4:end].splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        list_match = re.match(r"^\s*-\s+(.+)$", line)
        if active_key and list_match:
            data.setdefault(active_key, []).append(clean_value(list_match.group(1)))
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            continue
        key, value = match.groups()
        if value == "":
            data[key] = []
            active_key = key
        else:
            data[key] = clean_value(value)
            active_key = None
    return data


def clean_value(value: str):
    text = value.strip().strip("\"'")
    if text == "true":
        return True
    if text == "false":
        return False
    if text.startswith("[") and text.endswith("]"):
        return [clean_value(item) for item in text[1:-1].split(",") if item.strip()]
    return text


def validate_frontmatter_links(frontmatter: dict, entry: dict, label: str, ids: dict[str, set[str]]) -> None:
    reference_keys = {ref.get("key") for ref in entry.get("references", [])} | reference_keys_from_frontmatter(frontmatter)
    for key in as_list(frontmatter.get("references")):
        if key not in reference_keys:
            ERRORS.append(f"{label}: front matter reference {key} missing from referenceItems")
    for project_id in as_list(frontmatter.get("projects")):
        if project_id not in ids["projects"]:
            ERRORS.append(f"{label}: front matter project {project_id} missing from registry")
    for method_id in as_list(frontmatter.get("methods")):
        if method_id not in ids["methods"]:
            ERRORS.append(f"{label}: front matter method {method_id} missing from registry")
    hero = frontmatter.get("hero")
    if hero and entry.get("media"):
        roles = {item.get("role") for item in entry.get("media", {}).get("items", [])}
        ids = {item.get("id") for item in entry.get("media", {}).get("items", [])}
        if hero not in roles and hero not in ids:
            ERRORS.append(f"{label}: front matter hero {hero} missing from media roles")


def validate_citations(text: str, entry: dict, label: str) -> None:
    reference_keys = {ref.get("key") for ref in entry.get("references", [])}
    content = entry.get("content")
    if content:
        path = site_file_path(content)
        if path and path.exists():
            reference_keys |= reference_keys_from_frontmatter(parse_frontmatter(path.read_text(encoding="utf-8")))
    for key in re.findall(r"\[cite:([^\]]+)\]", text):
        if key not in reference_keys:
            ERRORS.append(f"{label}: citation {key} missing from referenceItems")


def validate_shortcodes(text: str, entry: dict, label: str) -> None:
    media_items = entry.get("media", {}).get("items", [])
    media_keys = {item.get("role") for item in media_items} | {item.get("id") for item in media_items}
    for shortcode, value in re.findall(r"\{\{\s*([a-zA-Z-]+):([^}]+)\s*\}\}", text):
        if shortcode == "figure" and media_items and value.strip() not in media_keys:
            ERRORS.append(f"{label}: figure shortcode {value.strip()} missing from media roles")
        if shortcode == "compare" and media_items:
            for part in [item.strip() for item in value.split(",") if item.strip()]:
                if "/" not in part and part not in media_keys:
                    ERRORS.append(f"{label}: compare shortcode {part} missing from media roles")


def reference_keys_from_frontmatter(frontmatter: dict) -> set[str]:
    keys = set(as_list(frontmatter.get("references")))
    for item in as_list(frontmatter.get("referenceItems")):
        key = str(item).split("|", 1)[0].strip()
        if key:
            keys.add(key)
    return keys


def validate_internal_link(link: str, prefix: str, content: str = "") -> None:
    if link.startswith(("http://", "https://", "mailto:", "#")):
        return
    target = link.split("#", 1)[0].split("?", 1)[0]
    if target:
        ensure_exists(resolve_content_path(target, content), prefix)


def resolve_content_path(path: str, content: str) -> str:
    if path.startswith(ROOT_PREFIX):
        return path[len(ROOT_PREFIX):]
    if re.match(r"^(?:[a-z]+:|/|assets/|content/|data/|meta/|pages/)", path, re.I):
        return path
    if not content:
        return path
    return str((Path(content).parent / path).as_posix())


def as_list(value) -> list:
    if value in (None, ""):
        return []
    return value if isinstance(value, list) else [value]


def validate_reading_paths(content: dict, ids: dict[str, set[str]]) -> None:
    for path_entry in content.get("readingPaths", []):
        for item in path_entry.get("items", []):
            bucket = bucket_for_type(item.get("type"))
            if not bucket or item.get("id") not in ids[bucket]:
                ERRORS.append(f"readingPath:{path_entry.get('id')}: missing {item.get('type')} {item.get('id')}")


def validate_methods(methods: list[dict], ids: dict[str, set[str]]) -> None:
    for method in methods:
        article = method.get("article")
        if article and article not in ids["articles"]:
            ERRORS.append(f"method:{method.get('id')}: linked article {article} does not exist")


def validate_related(related: dict, ids: dict[str, set[str]], label: str) -> None:
    for item_id in related.get("projects", []):
        if item_id not in ids["projects"]:
            ERRORS.append(f"{label}: related project {item_id} does not exist")
    for item_id in related.get("articles", []):
        if item_id not in ids["articles"]:
            ERRORS.append(f"{label}: related article {item_id} does not exist")
    for item_id in related.get("methods", []):
        if item_id not in ids["methods"]:
            ERRORS.append(f"{label}: related method {item_id} does not exist")


def validate_static_files() -> None:
    files = [
        "index.html",
        "pages/projects.html",
        "pages/project.html",
        "pages/knowledge.html",
        "pages/method.html",
        "pages/methods.html",
        "pages/about.html",
        "pages/404.html",
        "meta/robots.txt",
        "meta/sitemap.xml",
        "meta/feed.xml",
        "assets/profile.png",
    ]
    for file in files:
        ensure_exists(file, "missing static file")


def require_fields(obj: dict, label: str, fields: list[str]) -> None:
    for field in fields:
        if obj.get(field) in (None, "", []):
            ERRORS.append(f"{label}: missing {field}")


def ensure_exists(file: str, prefix: str) -> None:
    if not file:
        ERRORS.append(f"{prefix}: empty path")
        return
    path = site_file_path(file)
    if path is None:
        ERRORS.append(f"{prefix}: absolute path is outside site root and cannot be served: {file}")
        return
    if not path.exists():
        ERRORS.append(f"{prefix}: {file}")


def site_file_path(file: str) -> Path | None:
    path = Path(file)
    if path.is_absolute():
        file_posix = path.as_posix()
        if file_posix.startswith(ROOT_PREFIX):
            return ROOT / file_posix[len(ROOT_PREFIX):]
        return None
    return ROOT / path


def bucket_for_type(item_type: str | None) -> str | None:
    return {"project": "projects", "article": "articles", "method": "methods"}.get(item_type or "")


def read_json(file: str) -> dict:
    try:
        with (ROOT / file).open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:
        ERRORS.append(f"{file}: {exc}")
        return {}


if __name__ == "__main__":
    raise SystemExit(main())
