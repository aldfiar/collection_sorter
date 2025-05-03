from functools import lru_cache
from typing import Any, Dict, Optional, Callable

import pycountry


@lru_cache(maxsize=1)
def _get_languages():
    return {lang.name.lower() for lang in pycountry.languages}

def manga_template_function(
    info: Dict[str, Any], 
    symbol_replace_function: Optional[Callable[[str], str]] = None
) -> str:
    """Format manga information into a standardized filename.
    
    Args:
        info: Dictionary containing manga metadata
        symbol_replace_function: Optional function to clean up special characters
        
    Returns:
        Formatted filename string
    """
    author = info["author"]
    name = " ".join(info["name"].split())
    
    # Build author info section
    group = info.get("group")
    author_info = f"[{group} ({author})]" if group else f"[{author}]"
    
    # Check for language tag
    languages = _get_languages()
    language_tag = None
    if tags := info.get("tags"):
        language_tag = next(
            (tag for tag in tags if tag.lower() in languages),
            None
        )
    
    # Assemble template
    template = f"{author_info} {name}"
    if language_tag:
        template = f"{template} [{language_tag}]"

    return symbol_replace_function(template) if symbol_replace_function else template
