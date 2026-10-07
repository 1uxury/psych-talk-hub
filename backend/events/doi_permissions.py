"""Model permissions shared by DOI pages and their final transaction."""

VIEW_PERMISSIONS = ("events.view_event", "events.view_resource", "events.view_eventresource")
WRITE_PERMISSIONS = (*VIEW_PERMISSIONS, "events.change_event", "events.add_eventresource")


def can_import(user):
    return user.is_active and user.is_staff and user.has_perms(WRITE_PERMISSIONS)
