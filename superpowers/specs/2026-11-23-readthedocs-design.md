# Read the Docs pipeline for the CoreUI and AdminLTE themes

**Date:** 2026-11-23 · **Status:** draft for maintainer approval · **Repos:** django-crud-views-coreui,
django-crud-views-adminlte (same document in both).

## Intent

The docs pipeline, as for the Tabler theme: the existing `docs/` of both themes builds and publishes on Read the Docs, and
every pull request gets a Read the Docs preview build and check. Bringing the content in sync is a later wave.

## Goals

- Read the Docs projects `django-crud-views-coreui` and `django-crud-views-adminlte`, configured like
  `django-crud-views-tabler`: public, English, programming language "Only Words", default branch `main`, default version
  `latest`, connected through Read the Docs' GitHub App (no repository webhooks), pull-request builds on.
- `.readthedocs.yaml` in each repo, a copy of Tabler's (ubuntu-24.04, Python 3.12, `mkdocs.yml`,
  `docs/requirements.txt`).
- README: a Docs badge after the Coverage badge (Tabler's markup with the repo's slug); CoreUI's "not published yet"
  note becomes the plain link. The `Documentation` URLs in both `pyproject.toml` files already point at
  `https://django-crud-views-<theme>.readthedocs.io/en/latest/` and stay.

## Non-goals

- Doc content, navigation or the missing AdminLTE pages (branding, icons, layouts, crispy): the later sync wave.
- Versioned docs per release tag beyond Read the Docs' defaults; custom domains; changes to the Tabler project.
- Any change to the GitHub `docs.yml` workflow (it keeps building with `--strict` on every PR).

## Anti-goals

- The API token in any file, commit, log or PR text. It is read from a scratchpad file for the API calls and deleted
  afterwards; the maintainer rotates it when the wave is done.
- A project connected by a manual webhook instead of the GitHub App (it would differ from Tabler and break PR checks).

## Approaches

1. Port Tabler's setup; the maintainer imports both projects in the Read the Docs dashboard and turns on PR builds.
2. **Chosen:** the same, but the projects are created and configured through the Read the Docs API v3 with the
   maintainer's token.
3. GitHub Pages via `mkdocs gh-deploy`. Dropped: breaks the published Documentation URLs and diverges from Tabler.

## Design

1. **Maintainer, once:** add both repos to the "Read the Docs" GitHub App installation of jacob-consulting
   (organisation Settings → GitHub Apps → Read the Docs → Configure → Repository access), as Tabler already is. The
   API's remote-repository listing must then show both repos (today it shows only Tabler).
2. **API:** `POST /api/v3/projects/` per repo with name, repository URL (`type: git`), language `en`, programming
   language `words`, homepage the GitHub URL; then `PATCH` default branch `main` and pull-request builds on. Confirm with
   `GET` that the project is linked to the GitHub App remote repository like Tabler's.
3. **Repos (branch `docs/readthedocs`, one PR each):** `.readthedocs.yaml` and the README changes above. The PR itself is
   the end-to-end check: its Read the Docs check passes and the preview URL renders; after the merge, `latest` builds
   from `main` and `https://django-crud-views-<theme>.readthedocs.io/en/latest/` answers 200.

## Left to the builder

The exact API payloads, and the order of the project creation and the PR (the PR is opened after the project exists, so
its first push triggers a preview build).
