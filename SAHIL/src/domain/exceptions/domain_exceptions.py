from __future__ import annotations


class DomainError(Exception):
    """Base class for all business-rule violations. Never raise raw Exception in services."""


class EntityNotFoundError(DomainError):
    def __init__(self, entity: str, identifier: str) -> None:
        self.entity = entity
        self.identifier = identifier
        super().__init__(f"{entity} with identifier '{identifier}' was not found.")


class DuplicateEmailError(DomainError):
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"An account with email '{email}' already exists.")


class InvalidCredentialsError(DomainError):
    def __init__(self) -> None:
        super().__init__("Invalid email or password.")


class InactiveAccountError(DomainError):
    def __init__(self) -> None:
        super().__init__("This account has been deactivated. Contact your administrator.")


class InsufficientPermissionError(DomainError):
    def __init__(self, required_roles: list[str]) -> None:
        self.required_roles = required_roles
        super().__init__(f"This action requires one of the following roles: {', '.join(required_roles)}.")


class InvalidRolePromotionError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class DepartmentHierarchyCycleError(DomainError):
    def __init__(self) -> None:
        super().__init__("Assigning this parent department would create a circular hierarchy.")


class DepartmentInUseError(DomainError):
    def __init__(self, department_id: str) -> None:
        super().__init__(
            f"Department '{department_id}' cannot be deactivated while it has active employees or child departments."
        )


class DuplicateCategoryNameError(DomainError):
    def __init__(self, name: str) -> None:
        super().__init__(f"An asset category named '{name}' already exists.")


# --- Phase 2: Asset Registration & Directory --------------------------------

class DuplicateSerialNumberError(DomainError):
    def __init__(self, serial_number: str) -> None:
        self.serial_number = serial_number
        super().__init__(
            f"An asset with serial number '{serial_number}' is already registered. "
            "Each physical asset must have a unique serial number."
        )


class DuplicateAssetTagError(DomainError):
    def __init__(self, asset_tag: str) -> None:
        super().__init__(f"Asset tag '{asset_tag}' is already in use.")


class InvalidStateTransitionError(DomainError):
    def __init__(self, from_state: str, to_state: str) -> None:
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(f"Cannot transition asset from '{from_state}' to '{to_state}' — this move is not permitted.")


class InvalidCategoryError(DomainError):
    def __init__(self, category_id: str) -> None:
        super().__init__(f"Asset category '{category_id}' does not exist.")


# --- Phase 3: Allocation & Resource Booking ---------------------------------

class AssetNotBookableError(DomainError):
    def __init__(self, asset_id: str) -> None:
        super().__init__(f"Asset '{asset_id}' is not flagged as a shared/bookable resource.")


class AssetAlreadyAllocatedError(DomainError):
    """
    Raised when a direct allocation is attempted on an asset that already has
    an ACTIVE allocation. Carries the current holder's identity so the API/UI
    can render '...currently held by X' and offer a Transfer Request button,
    per the problem statement's Screen 5 conflict rule.
    """

    def __init__(self, asset_id: str, current_holder_user_id: str | None, current_holder_department_id: str | None) -> None:
        self.asset_id = asset_id
        self.current_holder_user_id = current_holder_user_id
        self.current_holder_department_id = current_holder_department_id
        super().__init__(
            f"Asset '{asset_id}' is already allocated and cannot be allocated again directly. "
            "Use a Transfer Request instead."
        )


class NoActiveAllocationError(DomainError):
    def __init__(self, asset_id: str) -> None:
        super().__init__(f"Asset '{asset_id}' has no active allocation to return or transfer.")


class TransferRequestNotPendingError(DomainError):
    def __init__(self, transfer_request_id: str) -> None:
        super().__init__(f"Transfer request '{transfer_request_id}' has already been resolved.")


class SlotOverlapError(DomainError):
    """
    Raised when a booking request's [start_time, end_time) interval overlaps
    an existing UPCOMING/ONGOING booking for the same resource. This mirrors,
    at the domain layer, a PostgreSQL EXCLUDE constraint violation — see
    migration 0003 and SqlAlchemyBookingRepository.create_booking for how the
    two are wired together.
    """

    def __init__(self, asset_id: str) -> None:
        self.asset_id = asset_id
        super().__init__(f"Resource '{asset_id}' already has a booking that overlaps this time slot.")


class InvalidBookingWindowError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class BookingNotCancellableError(DomainError):
    def __init__(self, booking_id: str) -> None:
        super().__init__(f"Booking '{booking_id}' cannot be cancelled from its current status.")


# --- Phase 4: Maintenance & Audits -------------------------------------------

class InvalidMaintenanceTransitionError(DomainError):
    def __init__(self, from_state: str, to_state: str) -> None:
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(
            f"Cannot move maintenance request from '{from_state}' to '{to_state}' — this move is not permitted."
        )


class DuplicateActiveMaintenanceRequestError(DomainError):
    def __init__(self, asset_id: str) -> None:
        self.asset_id = asset_id
        super().__init__(
            f"Asset '{asset_id}' already has an open maintenance request. "
            "Resolve or reject it before raising a new one."
        )


class AuditCycleClosedError(DomainError):
    def __init__(self, cycle_id: str) -> None:
        self.cycle_id = cycle_id
        super().__init__(f"Audit cycle '{cycle_id}' is closed; its findings can no longer be modified.")


class NotAnAssignedAuditorError(DomainError):
    def __init__(self, cycle_id: str) -> None:
        super().__init__(f"You are not an assigned auditor for audit cycle '{cycle_id}'.")


class AssetNotInAuditScopeError(DomainError):
    def __init__(self, asset_id: str, cycle_id: str) -> None:
        super().__init__(f"Asset '{asset_id}' is outside the department/location scope of audit cycle '{cycle_id}'.")
