from typing import Any, Dict

import pycountry

languages = [d.name for d in pycountry.languages]


def manga_template_function(info: Dict[str, Any], symbol_replace_function=None):
    author = info["author"]
    group = info.get("group")
    name = " ".join(info["name"].split())
    language_tag = None
    if "tags" in info:
        for tag in info["tags"]:
            if tag.title() in languages:
                language_tag = tag
    author_info = f"[{group} ({author})]" if group is not None else f"[{author}]"

    template = (
        f"{author_info} {name}"
        if language_tag is None
        else f"{author_info} {name} [{language_tag}]"
    )

    if symbol_replace_function:
        template = symbol_replace_function(template)

    return template
