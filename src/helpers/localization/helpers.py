from functools import lru_cache
from typing import List

import src.helpers.localization.en as _en
import src.helpers.localization.de as _de

_MODULES = {"en": _en, "de": _de}
_languages: List[str] = ["en"]


def init(project_root) -> None:
    """Called once from Project.__init__ to read the configured languages."""
    global _languages
    from src.core.configuration import parse_ducku_yaml
    _languages = parse_ducku_yaml(project_root).languages
    # Bust cached results so subsequent get_words calls use new languages
    get_words.cache_clear()
    get_content_keywords.cache_clear()


@lru_cache(maxsize=None)
def get_words(key: str) -> List[str]:
    """Return a deduplicated merged list for the given word-list key across configured languages."""
    seen = set()
    result = []
    for lang in _languages:
        module = _MODULES.get(lang)
        if not module:
            continue
        for word in getattr(module, key, []):
            if word not in seen:
                seen.add(word)
                result.append(word)
    return result


@lru_cache(maxsize=None)
def get_content_keywords(artifact_type: str) -> List[str]:
    """Return deduplicated merged keywords for the given artifact type across configured languages."""
    seen = set()
    result = []
    for lang in _languages:
        module = _MODULES.get(lang)
        if not module:
            continue
        for kw in module.CONTENT_CHECK_KEYWORDS.get(artifact_type, []):
            if kw not in seen:
                seen.add(kw)
                result.append(kw)
    return result
