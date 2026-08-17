"""Shared helpers for talking to the ephemeral test database directly, bypassing
the application's own connection pool. Kept out of conftest.py so it can be
imported from test modules too (see test_infra_smoke.py)."""

# Tables that hold reference data the application depends on, plus dbmate's own
# migration-tracking table. Truncating them between tests would either wipe seed
# data (role_types, related_types, avatars — see db/migrations/) or make dbmate
# think its migrations need re-applying. Keep this in sync with db/migrations/
# when a new reference table is added (see spec: "Una tabla nueva queda cubierta
# sin tocar la infraestructura").
PRESERVED_TABLES = frozenset({"role_types", "related_types", "avatars", "schema_migrations"})


async def truncate_mutable_tables(conn) -> None:
    """Vacía todas las tablas mutables del esquema, dejando intactas las de
    referencia y la de control de migraciones (design D4). La lista de tablas a
    truncar se deriva del esquema en tiempo de ejecución: una tabla nueva queda
    cubierta automáticamente."""
    rows = await conn.fetch(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
    )
    tables = [r["tablename"] for r in rows if r["tablename"] not in PRESERVED_TABLES]
    if not tables:
        return
    quoted = ", ".join(f'"{t}"' for t in tables)
    # A single statement, not wrapped in an explicit transaction of its own beyond
    # what TRUNCATE itself opens and commits immediately: this runs *before* the
    # test, never around it (design D4).
    await conn.execute(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE")
