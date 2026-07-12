from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status

from src.application.services.booking_service import BookingService
from src.domain.entities.user import User
from src.domain.exceptions.domain_exceptions import EntityNotFoundError
from src.presentation.api.v1.schemas.booking_schemas import BookingResponse, CreateBookingRequest
from src.presentation.dependencies import get_booking_service
from src.presentation.middleware.auth_middleware import require_any_authenticated

router = APIRouter(tags=["Resource Booking"])


@router.post("/assets/{asset_id}/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def book_resource(
    asset_id: uuid.UUID,
    payload: CreateBookingRequest,
    acting_user: User = Depends(require_any_authenticated),
    service: BookingService = Depends(get_booking_service),
) -> BookingResponse:
    """
    Books a time slot on a shared/bookable resource. Returns 409 if the slot
    overlaps an existing UPCOMING/ONGOING booking — enforced atomically by a
    PostgreSQL EXCLUDE constraint, not just an application-level check.
    """
    booking = await service.book_resource(
        acting_user=acting_user,
        asset_id=asset_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        department_id=payload.department_id,
        purpose=payload.purpose,
    )
    return BookingResponse.model_validate(booking)


@router.get("/assets/{asset_id}/bookings", response_model=list[BookingResponse])
async def get_calendar_for_asset(
    asset_id: uuid.UUID,
    from_time: datetime | None = Query(default=None),
    to_time: datetime | None = Query(default=None),
    _: User = Depends(require_any_authenticated),
    service: BookingService = Depends(get_booking_service),
) -> list[BookingResponse]:
    """Calendar view of a resource's existing bookings, optionally windowed by from_time/to_time."""
    bookings = await service.get_calendar_for_asset(asset_id, from_time, to_time)
    return [BookingResponse.model_validate(b) for b in bookings]


@router.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: uuid.UUID,
    _: User = Depends(require_any_authenticated),
    service: BookingService = Depends(get_booking_service),
) -> BookingResponse:
    booking = await service.get_booking(booking_id)
    if booking is None:
        raise EntityNotFoundError("Booking", str(booking_id))
    return BookingResponse.model_validate(booking)


@router.post("/bookings/{booking_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
    booking_id: uuid.UUID,
    acting_user: User = Depends(require_any_authenticated),
    service: BookingService = Depends(get_booking_service),
) -> None:
    await service.cancel_booking(acting_user=acting_user, booking_id=booking_id)
