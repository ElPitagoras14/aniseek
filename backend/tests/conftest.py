"""Test infrastructure for the backend suite (see openspec/changes/add-backend-testing).

Design summary (full rationale in the change's design.md):
- D2: pytest starts and tears down a real, ephemeral PostgreSQL container itself.
- D3: its schema is built by running dbmate against dbmate/migrations/, the same
  artifact that builds the production schema.
- D4: isolation between tests is by truncating mutable tables, never by wrapping
  a test in a transaction — that would degrade the transaction under test to a
  savepoint and hide exactly what these tests exist to verify.
- D5: the application resolves its settings at import time, so the ephemeral
  database has to exist and the environment variables have to be set *before*
  pytest collects any test module. That has to happen in pytest_configure,
  which runs before collection — a fixture would run too late.

Windows note (unify-database-access): psycopg3's async mode refuses to run on
asyncio's default `ProactorEventLoop` on Windows. The engine only needs
`SelectorEventLoop`-compatible behavior (no subprocess/pipe support), so the
policy is switched process-wide before any event loop is created. Irrelevant
on Linux, where production and CI run.
"""

import asyncio
import os
import shutil
import sys
import tempfile

import asyncpg
import pytest
from dbutils import truncate_mutable_tables
from testcontainers.community.postgres import PostgresContainer
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_DBMATE_SOURCE_DIR = os.path.join(_REPO_ROOT, "dbmate")

# Same major version as production (see compose.dev.yaml's aniseek-db service).
_POSTGRES_IMAGE = "postgres:18.1-alpine"
_DB_ALIAS = "aniseek-test-db"

_network: Network | None = None
_postgres: PostgresContainer | None = None
_animes_folder: str | None = None
# asyncpg parses its own DSN and doesn't understand SQLAlchemy's "+driver"
# suffix, so the raw pool below keeps a bare "postgresql://" URL, separate
# from the app's DB_URL (which needs "+psycopg" — see unify-database-access).
_raw_dsn: str | None = None


def _apply_migrations() -> None:
    """Build the schema the same way production does: run dbmate against the
    ephemeral database (design D3). If `adopt-dbmate` is ever replaced, this is
    the single point to change."""
    migrate = DockerContainer("ghcr.io/amacneil/dbmate")
    migrate.with_network(_network)
    migrate.with_command(["--no-dump-schema", "up"])
    migrate.with_env(
        "DATABASE_URL",
        f"postgresql://{_postgres.username}:{_postgres.password}"
        f"@{_DB_ALIAS}:5432/{_postgres.dbname}?sslmode=disable",
    )
    migrate.with_volume_mapping(_DBMATE_SOURCE_DIR, "/db", "ro")
    migrate.start()
    try:
        exit_code = migrate.wait()
        if exit_code != 0:
            stdout, stderr = migrate.get_logs()
            raise RuntimeError(
                f"dbmate migration failed (exit {exit_code}):\n"
                f"{stdout.decode(errors='replace')}\n{stderr.decode(errors='replace')}"
            )
    finally:
        migrate.stop()


def pytest_configure(config: pytest.Config) -> None:
    global _network, _postgres, _animes_folder, _raw_dsn

    _network = Network()
    _network.create()

    _postgres = PostgresContainer(_POSTGRES_IMAGE)
    _postgres.with_network(_network)
    _postgres.with_network_aliases(_DB_ALIAS)
    _postgres.start()

    _apply_migrations()

    _animes_folder = tempfile.mkdtemp(prefix="aniseek-test-animes-")
    _raw_dsn = _postgres.get_connection_url(driver=None)

    # Fixed before any application module is imported (design D5). Every
    # BaseSettings subclass in src/ is covered here — see the config.py files
    # under src/, src/database/, and src/packages/*/. Same scheme as
    # production (unify-database-access): a single DB_URL, unchanged, works
    # for the app's async engine.
    os.environ["DB_URL"] = _postgres.get_connection_url(driver="psycopg")
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["ALGORITHM"] = "HS256"
    os.environ["REDIS_URL"] = "redis://localhost:6379"
    os.environ["ACCESS_TOKEN_EXP_MIN"] = "60"
    os.environ["REFRESH_TOKEN_EXP_DAY"] = "10"
    os.environ["ANIMES_FOLDER"] = _animes_folder


def pytest_unconfigure(config: pytest.Config) -> None:
    if _postgres is not None:
        _postgres.stop()
    if _network is not None:
        _network.remove()
    if _animes_folder is not None:
        shutil.rmtree(_animes_folder, ignore_errors=True)


@pytest.fixture(scope="session", autouse=True)
async def _app_db_pool():
    """Verifies the application's own engine (`database.client.engine`) can reach
    the database, for the whole session. Deferred import: config resolves on
    import, so this has to happen after pytest_configure, not at module load
    time."""
    from database.client import connect_db, disconnect_db

    await connect_db()
    try:
        yield
    finally:
        await disconnect_db()


@pytest.fixture(scope="session")
def raw_dsn() -> str:
    """The bare "postgresql://" DSN (see `_raw_dsn` above), for tests that need
    to open a connection asyncpg can parse directly instead of going through
    `DB_URL`."""
    return _raw_dsn


@pytest.fixture(scope="session")
async def pg_pool():
    """A connection pool independent from the application's own engine, used to
    seed/inspect data directly and, in the isolation checks, to prove that a
    write made through the app's engine is visible from an unrelated
    connection. Uses `_raw_dsn` (bare "postgresql://"), not `DB_URL`: asyncpg
    doesn't understand the "+psycopg" driver suffix the app needs."""
    pool = await asyncpg.create_pool(dsn=_raw_dsn)
    try:
        yield pool
    finally:
        await pool.close()


@pytest.fixture
async def raw_conn(pg_pool):
    async with pg_pool.acquire() as conn:
        yield conn


@pytest.fixture(autouse=True)
async def _clean_db(pg_pool):
    """Vacía las tablas mutables antes de cada prueba (design D4), no envuelve
    la prueba en una transacción."""
    async with pg_pool.acquire() as conn:
        await truncate_mutable_tables(conn)


@pytest.fixture
def mock_dramatiq(monkeypatch):
    """Substitutes the two Dramatiq sends the transactional paths make
    (design D6): without this, tests would need a running Redis and would
    publish real messages. Returns the two mocks so tests can assert on them."""
    from unittest.mock import Mock

    from worker import download_anime_episode, order_franchise

    download_send = Mock(return_value=Mock(message_id="test-job-id"))
    order_send = Mock()
    monkeypatch.setattr(download_anime_episode, "send", download_send)
    monkeypatch.setattr(order_franchise, "send", order_send)

    return {"download_anime_episode": download_send, "order_franchise": order_send}
