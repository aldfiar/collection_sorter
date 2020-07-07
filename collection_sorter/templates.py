from typing import Dict, Any

import pycountry

languages = [d.name for d in pycountry.languages]


def base_manga_template(info: Dict[str, Any], linux=True):
    author_raw = info["author"]
    if "." in author_raw:
        author_raw = author_raw.replace(".", "")
    author = author_raw
    group = info.get("group")
    name = " ".join(info["name"].split())
    language_tag = None
    if 'tags' in info:
        for tag in info["tags"]:
            if tag.title() in languages:
                language_tag = tag
    author_info = f"[{group} ({author})]" if group is not None else f"[{author}]"

    template = f"{author_info} {name}" if language_tag is None else f"{author_info} {name} [{language_tag}]"

    if linux:
        template = template.replace(" ", "_")

    return template
