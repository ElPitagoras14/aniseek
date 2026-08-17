"""Atomicity of the transaction in packages/franchises/service.py, plus the
positive case (design D6, scenario "Sin fallo, todas las escrituras
persisten"): without it, an implementation that never committed anything
would pass every failure-injection test above unnoticed.
"""

import pytest
from factories import create_anime


async def _boom(*args, **kwargs):
    raise RuntimeError("boom")


async def test_create_franchise_leaves_no_trace_on_mid_transaction_failure(
    raw_conn, monkeypatch
):
    from packages.franchises import repository, service
    from packages.franchises.schemas import FranchiseCreate

    anime_id = await create_anime(raw_conn, franchise_id=None)

    # First write is insert_franchise; interrupt on the next one.
    monkeypatch.setattr(repository, "assign_animes_to_franchise", _boom)

    franchise_info = FranchiseCreate(
        franchise="My Franchise", animes=[{"id": anime_id, "season": 1}]
    )

    with pytest.raises(RuntimeError, match="boom"):
        await service.create_franchise_controller(franchise_info)

    franchise_row = await raw_conn.fetchrow(
        "SELECT id FROM franchises WHERE name = $1", "My Franchise"
    )
    anime_row = await raw_conn.fetchrow(
        "SELECT franchise_id FROM animes WHERE id = $1", anime_id
    )
    assert franchise_row is None
    assert anime_row["franchise_id"] is None


async def test_create_franchise_persists_everything_without_a_failure(
    mock_dramatiq, raw_conn
):
    from packages.franchises import service
    from packages.franchises.schemas import FranchiseCreate

    anime_id = await create_anime(raw_conn, franchise_id=None)

    franchise_info = FranchiseCreate(
        franchise="Positive Franchise", animes=[{"id": anime_id, "season": 2}]
    )

    await service.create_franchise_controller(franchise_info)

    franchise_row = await raw_conn.fetchrow(
        "SELECT id, name FROM franchises WHERE name = $1", "Positive Franchise"
    )
    anime_row = await raw_conn.fetchrow(
        "SELECT franchise_id FROM animes WHERE id = $1", anime_id
    )
    assert franchise_row is not None
    assert anime_row["franchise_id"] == franchise_row["id"]
    mock_dramatiq["order_franchise"].assert_called_once()
