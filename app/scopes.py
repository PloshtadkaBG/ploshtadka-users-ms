from enum import StrEnum


class UserScope(StrEnum):
    READ = "users:read"
    ME = "users:me"
    ADMIN = "admin:users"


class VenueScope(StrEnum):
    READ = "venues:read"
    ME = "venues:me"
    WRITE = "venues:write"
    DELETE = "venues:delete"
    IMAGES = "venues:images"
    SCHEDULE = "venues:schedule"

    ADMIN = "admin:venues"
    ADMIN_READ = "admin:venues:read"
    ADMIN_WRITE = "admin:venues:write"
    ADMIN_DELETE = "admin:venues:delete"


class BookingScope(StrEnum):
    # Customer scopes
    READ = "bookings:read"  # view own bookings
    WRITE = "bookings:write"  # create a booking
    CANCEL = "bookings:cancel"  # cancel own booking

    # Venue owner scopes
    MANAGE = "bookings:manage"  # confirm / complete / no_show for own venue's bookings

    # Admin scopes
    ADMIN = "admin:bookings"
    ADMIN_READ = "admin:bookings:read"
    ADMIN_WRITE = "admin:bookings:write"
    ADMIN_DELETE = "admin:bookings:delete"


USER_SCOPES_DESCS: dict[str, str] = {
    UserScope.READ: "Read users data.",
    UserScope.ME: "Read current user profile.",
    UserScope.ADMIN: "Perform any user operation (admin).",
}

VENUE_SCOPES_DESCRIPTIONS: dict[str, str] = {
    VenueScope.READ: "Browse and search public venue listings.",
    VenueScope.ME: "Read your own venues and their details.",
    VenueScope.WRITE: "Create and update your own venues.",
    VenueScope.DELETE: "Delete your own venues.",
    VenueScope.IMAGES: "Upload and manage images for your own venues.",
    VenueScope.SCHEDULE: "Manage unavailability windows for your own venues.",
    VenueScope.ADMIN: "Perform any venue operation (admin)",
    VenueScope.ADMIN_READ: "Read any venue regardless of status (admin).",
    VenueScope.ADMIN_WRITE: "Edit any venue and change its status (admin).",
    VenueScope.ADMIN_DELETE: "Hard-delete any venue (admin).",
}

BOOKING_SCOPE_DESCRIPTIONS: dict[str, str] = {
    BookingScope.READ: "View your own bookings.",
    BookingScope.WRITE: "Create a new booking at a venue.",
    BookingScope.CANCEL: "Cancel your own pending or confirmed booking.",
    BookingScope.MANAGE: "Confirm, complete, or mark no-show on your venue bookings.",
    BookingScope.ADMIN_READ: "Read any booking regardless of owner (admin).",
    BookingScope.ADMIN_WRITE: "Modify any booking status (admin).",
    BookingScope.ADMIN_DELETE: "Hard-delete any booking (admin).",
}

SCOPE_DESCS = VENUE_SCOPES_DESCRIPTIONS | USER_SCOPES_DESCS | BOOKING_SCOPE_DESCRIPTIONS
DEFAULT_USER_SCOPES = [
    UserScope.ME,
    VenueScope.READ,
    BookingScope.READ,
    BookingScope.WRITE,
    BookingScope.CANCEL,
]
DEFAULT_OWNER_SCOPES = DEFAULT_USER_SCOPES + [
    VenueScope.ME,
    VenueScope.WRITE,
    VenueScope.DELETE,
    VenueScope.IMAGES,
    VenueScope.SCHEDULE,
    BookingScope.MANAGE,
]
DEFAULT_ADMIN_SCOPES = [UserScope.ADMIN, VenueScope.ADMIN, BookingScope.ADMIN]
