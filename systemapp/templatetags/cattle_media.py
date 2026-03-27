from __future__ import annotations

import hashlib

from django import template
from django.conf import settings

register = template.Library()


_FALLBACK_COW_IMAGES = [
    # Keep this list strict: only verified cattle photos (avoid landscapes / blanks).
    "https://images.unsplash.com/photo-1500595046743-cd271d694d30?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1527153857715-3908f2bae5e8?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1545468800-85cc9bc6ecf7?q=80&w=1200&auto=format&fit=crop",
]

_FALLBACK_BUFFALO_IMAGES = [
    # If a buffalo-specific photo isn't available, reuse cattle photos (still real).
    "https://images.unsplash.com/photo-1527153857715-3908f2bae5e8?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1500595046743-cd271d694d30?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1545468800-85cc9bc6ecf7?q=80&w=1200&auto=format&fit=crop",
]


def _stable_index(key: str, length: int) -> int:
    if length <= 0:
        return 0
    digest = hashlib.sha256((key or "cattle").encode("utf-8")).digest()
    return digest[0] % length


@register.filter(name="cattle_image_url")
def cattle_image_url(cattle) -> str:
    """
    Return a consistent image URL for a cattle object across pages:
    1) use `cattle.image.url` if present
    2) use a local MEDIA file matching tag_id (cattle_images/<TAG>.<ext>)
    3) fall back to a stable Unsplash photo based on tag_id
    """
    if cattle is None:
        return _FALLBACK_COW_IMAGES[0]

    # 1) Model image
    try:
        image_field = getattr(cattle, "image", None)
        if image_field and getattr(image_field, "url", ""):
            return image_field.url
    except Exception:
        pass

    tag_id = (getattr(cattle, "tag_id", "") or "").strip() or str(getattr(cattle, "id", ""))

    cattle_type = (getattr(cattle, "cattle_type", "") or "").strip().upper()
    is_buffalo = cattle_type == "BUFFALO"

    # 2) Stable fallback (by tag_id so the same cattle shows the same image everywhere)
    images = _FALLBACK_BUFFALO_IMAGES if is_buffalo else _FALLBACK_COW_IMAGES
    return images[_stable_index(tag_id, len(images))]
