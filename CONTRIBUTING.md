# Contributing

See [docs/development.md](docs/development.md) for how to build, run and test the project, and [docs/architecture.md](docs/architecture.md) for how the pieces fit together.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) in English with a short description (e.g. `feat(frontend): add mobile bottom navigation`).

## Releases

The release version lives only in the `VERSION` file at the repository root. The `version` fields in `backend/pyproject.toml`, `worker/pyproject.toml` and `frontend/package.json` are frozen and not part of the release.

To publish a release, bump `VERSION` to a strictly greater semver value and merge it into `main`. The `release.yml` pipeline runs on that push and compares against the highest tag already published. Include the bump in the same PR as the change that warrants the release.

## Pinned dbmate version

The dbmate version is pinned to `2.35.0` on purpose. The migrate image is rebuilt on every version bump, so an untagged base would quietly pull a different dbmate into the one startup step that writes to the database.

Four places declare the version — `dbmate/Dockerfile`, `compose.dev.yaml`, `backend/tests/conftest.py`, and the `pg_dump` command in [docs/upgrading.md](docs/upgrading.md). `grep -rn "amacneil/dbmate"` finds them all. Raising dbmate means changing all four together; the natural moment is the commit that bumps `VERSION`, since that commit triggers the rebuild.

## `pg_dump` and the Postgres version

The migrate image also carries the `pg_dump` used to generate `dbmate/schema.sql`, and `pg_dump` must be at or above the server version — today `18.4` against `postgres:18.1-alpine`. **Raising the Postgres version means checking that the pinned image's client still reaches it**, and bumping dbmate along with it if it doesn't.
