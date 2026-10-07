"""Database sessions whose DOI namespace is written only by the preview service."""

from asgiref.sync import sync_to_async
from django.contrib.sessions.backends.base import UpdateError
from django.contrib.sessions.backends.db import SessionStore as DatabaseSessionStore
from django.db import transaction


PREVIEW_KEY = "doi_previews"


class SessionStore(DatabaseSessionStore):
    def save(self, must_create=False):
        # Force lazy loading before selecting the key (load can invalidate it).
        data = self._get_session(no_load=must_create)
        if self.session_key is None or must_create:
            data.pop(PREVIEW_KEY, None)
            return super().save(must_create=must_create)
        with transaction.atomic():
            row = self.model.objects.select_for_update().filter(
                session_key=self.session_key
            ).first()
            if row is None:
                raise UpdateError
            current = self.decode(row.session_data)
            # Even a stale unrelated request or SAVE_EVERY_REQUEST must not
            # overwrite another tab's previews or resurrect a cancelled one.
            data.pop(PREVIEW_KEY, None)
            if PREVIEW_KEY in current:
                data[PREVIEW_KEY] = current[PREVIEW_KEY]
            return super().save(must_create=False)

    async def asave(self, must_create=False):
        return await sync_to_async(self.save)(must_create=must_create)
