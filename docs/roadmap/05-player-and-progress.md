# Phase 5: Player and watch progress

**Status:** not started. **Depends on:** nothing technically; benefits from Phases 0 and 3.

## Goal

Turn the app from a downloader into a place to watch: play downloaded episodes inside the app and remember where each user stopped.

## Current state (verified 2026-10-16)

- There is no built-in player. The Play button in `frontend/src/features/anime/components/episodes-table.tsx` opens the external episode URL (`ep.url`).
- The API already serves the downloaded file at `GET /episodes/{anime_id}/{episode_number}/file` (`backend/src/packages/episodes/router.py:110`). Whether it supports HTTP range requests was not verified.
- Per-user episode state today is only "downloaded by me / by another user" (`EpisodeInfo.is_user_downloaded` / `is_global_downloaded`).

## Scope

- Integrated player on top of the `/file` endpoint, with seeking through range requests.
- Watch progress per user: watched, pending, continue where you left off (new table keyed by user and episode).
- Subtitles and multiple audio tracks.
- Optional transcoding for devices that cannot play the downloaded format.
- Mobile layout: the app already has responsive views and bottom navigation (OpenSpec changes `mobile-bottom-navigation` and `mobile-responsive-views`).

## Open questions

- Download formats actually produced by the supported servers, and which need transcoding.
- Whether the player respects roles (members and above only; Phase 0 removed `guest`).
- Storage of progress and the privacy of one user's progress from others.
