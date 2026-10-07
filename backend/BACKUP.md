# Manual production backup and isolated restore

Verified on **7 October 2026** after explicit user approval. The production
database remains on the existing Free Frankfurt PostgreSQL 17 resource.
It expires **3 November 2026, 23:33 GMT**; Free has no managed backups.

The verified custom-format dump is stored outside this repository:
`G:\STUDY\psych-talk-hub-backups\psychtalk-20261007T003052Z.dump`
(43,568 bytes). It includes private administrator password hashes and database
sessions. The task-created dumps have protected Windows ACLs for their owner, SYSTEM
and Administrators only. Keep them private; do not
upload it with the public project or show its contents in a recording.

## Repeated export

1. Obtain explicit authorization for production data export, its private
   destination and temporary access-rule changes. Read the existing external
   access rules first and preserve them for a `finally` restoration.
2. Temporarily allow only the operator's current IPv4 `/32`. Use the verified
   external connection for the existing database; pass credentials privately
   through PostgreSQL environment variables, never as command-line arguments
   or console output. Require `PGSSLMODE=require` or stronger.
3. Verify `current_database() = psych_talk_prod`, PostgreSQL major version 17
   and active TLS. Use PostgreSQL 17 `pg_dump --format=custom --no-owner
   --no-acl --file=<private path outside Git>` with the production PGDATABASE.
   This is a read/export operation; never run production application tests.
4. Restore the original external access rules immediately, including on failure.
   The service continues to use its existing internal connection.

## Restore verification

Use only a newly created disposable **local PostgreSQL 17** database at
`127.0.0.1:5433`, e.g. `test_psychtalk_restore_<date>`. Verify it does not already
exist. Use local credentials and PGDATABASE for this restore; never restore
over development, production or PostgreSQL 11.

Run PostgreSQL 17 `pg_restore --no-owner --no-acl --exit-on-error
--dbname=<disposable local name> <private dump>`. Compare every column and ID
in Event, Resource, EventResource, auth_user and django_migrations against the
controlled source snapshot; compare aware timestamps in UTC. Destroy only the
explicitly verified disposable database after checking and record the result.
Keep the exported backup outside Git.

The latest verification matched **2 events, 6 resources, 6 associations,
1 administrator and 21 migration records**, including every field. The
temporary restore database was deleted and production external access rules
returned to `[]`. This verifies export and local restoration; it does not
provision a replacement hosted database or promise ongoing automated backups.
