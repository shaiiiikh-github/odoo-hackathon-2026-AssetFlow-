from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass
class AssetCategory:
    """
    custom_fields_schema holds category-specific optional fields as a JSON schema
    fragment, e.g. {"warranty_period_months": {"type": "integer", "required": false}}
    for Electronics. Kept generic so new categories don't require migrations.
    """

    id: UUID
    name: str
    custom_fields_schema: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
