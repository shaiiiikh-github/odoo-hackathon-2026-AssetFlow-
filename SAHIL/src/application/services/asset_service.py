from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from src.application.interfaces.i_unit_of_work import IUnitOfWork
from src.application.interfaces.repositories.i_asset_repository import AssetSearchFilters, AssetSearchResult
from src.domain.entities.asset import Asset, AssetCondition, AssetStatus
from src.domain.entities.user import User
from src.domain.exceptions.domain_exceptions import (
    DuplicateSerialNumberError,
    EntityNotFoundError,
    InsufficientPermissionError,
    InvalidCategoryError,
)
from src.domain.state_machines.asset_state_machine import AssetStateMachine


class AssetService:
    """
    Owns the full asset lifecycle: registration, lookup, search, and every
    status transition. State changes NEVER touch `asset.status` directly —
    they always route through AssetStateMachine.transition(), and every
    successful transition is appended to the immutable history log in the
    same DB transaction as the status update (so history can never drift
    out of sync with the live status).
    """

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    # ---------------------------------------------------------------- Registration
    async def register_asset(
        self,
        *,
        acting_user: User,
        name: str,
        category_id: uuid.UUID,
        serial_number: str,
        condition: AssetCondition,
        location: str,
        is_bookable: bool,
        acquisition_date: date | None,
        acquisition_cost: Decimal | None,
        department_id: uuid.UUID | None,
        photo_url: str | None,
        document_urls: list[str],
    ) -> Asset:
        if not acting_user.can_manage_assets():
            raise InsufficientPermissionError(required_roles=["ADMIN", "ASSET_MANAGER"])

        normalized_serial = serial_number.strip()

        async with self._uow as uow:
            category = await uow.categories.get_by_id(category_id)
            if category is None:
                raise InvalidCategoryError(str(category_id))

            # --- Edge case: duplicate serial number ---------------------------------
            # Checked here BEFORE insert so the Asset Manager gets a clean 409 with
            # a clear message instead of a raw DB IntegrityError. The unique index
            # on assets.serial_number (see migration) is the actual source of truth
            # and closes the race window this pre-check can't fully cover — see
            # note below on why both layers matter.
            existing = await uow.assets.get_by_serial_number(normalized_serial)
            if existing is not None:
                raise DuplicateSerialNumberError(normalized_serial)

            asset_tag = await uow.assets.next_asset_tag()

            asset = Asset(
                id=uuid.uuid4(),
                asset_tag=asset_tag,
                serial_number=normalized_serial,
                name=name.strip(),
                category_id=category_id,
                status=AssetStatus.AVAILABLE,
                condition=condition,
                location=location.strip(),
                is_bookable=is_bookable,
                acquisition_date=acquisition_date,
                acquisition_cost=acquisition_cost,
                department_id=department_id,
                photo_url=photo_url,
                document_urls=document_urls,
            )

            try:
                created = await uow.assets.add(asset)
            except Exception as exc:
                # Second line of defense: if two requests both passed the
                # pre-check above in the same instant (TOCTOU race), the
                # unique constraint on serial_number rejects the second
                # INSERT at the DB level. We translate that low-level
                # IntegrityError into the same clean domain error the
                # pre-check would have raised, so the API response is
                # identical either way — the caller never sees a raw SQL error.
                if _is_unique_violation(exc, "serial_number"):
                    raise DuplicateSerialNumberError(normalized_serial) from exc
                raise

            await uow.assets.record_state_transition(
                asset_id=created.id,
                from_state=AssetStatus.AVAILABLE,
                to_state=AssetStatus.AVAILABLE,
                triggered_by_user_id=acting_user.id,
                reason="Initial registration",
            )
            await uow.commit()
            return created

    # ---------------------------------------------------------------- Lookup / Search
    async def get_asset(self, asset_id: uuid.UUID) -> Asset:
        async with self._uow as uow:
            asset = await uow.assets.get_by_id(asset_id)
        if asset is None:
            raise EntityNotFoundError("Asset", str(asset_id))
        return asset

    async def search_assets(self, filters: AssetSearchFilters) -> AssetSearchResult:
        async with self._uow as uow:
            return await uow.assets.search(filters)

    async def get_state_history(self, asset_id: uuid.UUID) -> list[dict]:
        async with self._uow as uow:
            asset = await uow.assets.get_by_id(asset_id)
            if asset is None:
                raise EntityNotFoundError("Asset", str(asset_id))
            return await uow.assets.get_state_history(asset_id)

    # ---------------------------------------------------------------- Editing (non-status fields)
    async def update_asset_details(
        self,
        *,
        acting_user: User,
        asset_id: uuid.UUID,
        name: str | None,
        condition: AssetCondition | None,
        location: str | None,
        is_bookable: bool | None,
        department_id: uuid.UUID | None,
        photo_url: str | None,
        document_urls: list[str] | None,
    ) -> Asset:
        if not acting_user.can_manage_assets():
            raise InsufficientPermissionError(required_roles=["ADMIN", "ASSET_MANAGER"])

        async with self._uow as uow:
            asset = await uow.assets.get_by_id(asset_id)
            if asset is None:
                raise EntityNotFoundError("Asset", str(asset_id))

            if name is not None:
                asset.name = name.strip()
            if condition is not None:
                asset.condition = condition
            if location is not None:
                asset.location = location.strip()
            if is_bookable is not None:
                asset.is_bookable = is_bookable
            if department_id is not None:
                asset.department_id = department_id
            if photo_url is not None:
                asset.photo_url = photo_url
            if document_urls is not None:
                asset.document_urls = document_urls

            updated = await uow.assets.update(asset)
            await uow.commit()
            return updated

    # ---------------------------------------------------------------- State transitions
    async def transition_asset_status(
        self, *, acting_user: User, asset_id: uuid.UUID, to_state: AssetStatus, reason: str | None
    ) -> Asset:
        """
        The ONLY method in the codebase that changes asset.status. Uses
        SELECT ... FOR UPDATE to serialize concurrent transition attempts
        on the same asset (e.g. an Asset Manager approving maintenance at
        the same instant a Department Head marks it Lost during an audit) —
        without the lock, both could read the same starting state and both
        succeed, corrupting the state machine's guarantee.
        """
        if not acting_user.can_manage_assets():
            raise InsufficientPermissionError(required_roles=["ADMIN", "ASSET_MANAGER"])

        async with self._uow as uow:
            asset = await uow.assets.get_by_id_for_update(asset_id)
            if asset is None:
                raise EntityNotFoundError("Asset", str(asset_id))

            from_state = asset.status
            AssetStateMachine.transition(asset, to_state)  # raises InvalidStateTransitionError if illegal

            updated = await uow.assets.update(asset)
            await uow.assets.record_state_transition(
                asset_id=asset.id,
                from_state=from_state,
                to_state=to_state,
                triggered_by_user_id=acting_user.id,
                reason=reason,
            )
            await uow.commit()
            return updated


def _is_unique_violation(exc: Exception, column_hint: str) -> bool:
    """
    Best-effort check that a raised exception is a Postgres unique-constraint
    violation on the given column, without importing asyncpg/psycopg error
    types directly into the service layer (keeps this file DB-driver agnostic).
    """
    message = str(getattr(exc, "orig", exc)).lower()
    return "unique" in message and column_hint in message
