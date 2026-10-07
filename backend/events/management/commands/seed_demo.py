"""Manual management entry point; never called during startup or deployment."""

from json import JSONDecodeError

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError

from events.demo_seed import seed_demo_data


class Command(BaseCommand):
    help = "Fill missing fictional talks and verified reading; never overwrite edits."
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument("--fill-missing-covers", action="store_true",
                            help="Also fill empty covers on unchanged-title fictional demo talks; never replace existing images or descriptions.")

    def handle(self, *args, **options):
        try:
            created = seed_demo_data(fill_missing_covers=True) if options["fill_missing_covers"] else seed_demo_data()
        except (ValidationError, DatabaseError, OSError, JSONDecodeError) as error:
            raise CommandError(
                "Demo import failed; no partial import was saved. "
                "Check configuration, migrations and the demo manifest."
            ) from error
        self.stdout.write(self.style.SUCCESS(
            "Demo import complete. Created: "
            f"{created['events']} talks, {created['resources']} resources, "
            f"{created['associations']} reading links. Existing records were kept."
        ))
        if options["fill_missing_covers"]:
            self.stdout.write(f"Filled {created['covers']} existing empty demo covers.")
