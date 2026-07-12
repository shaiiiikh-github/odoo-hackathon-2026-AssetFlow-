from __future__ import annotations

import re

_ASSET_TAG_PATTERN = re.compile(r"^AF-\d{4,}$")


class AssetTag:
    """
    Formats and validates the AF-0001 style tag. Generation of the NEXT tag
    is deliberately NOT done here — that requires an atomic, race-safe
    counter, which lives in the database (a Postgres SEQUENCE), not in
    application code. See SqlAlchemyAssetRepository.next_asset_tag().
    """

    PREFIX = "AF-"

    @staticmethod
    def format(sequence_value: int) -> str:
        return f"{AssetTag.PREFIX}{sequence_value:04d}"

    @staticmethod
    def is_valid(tag: str) -> bool:
        return bool(_ASSET_TAG_PATTERN.match(tag))
