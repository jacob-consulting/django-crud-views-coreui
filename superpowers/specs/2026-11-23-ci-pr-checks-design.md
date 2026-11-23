# CI: PR checks for the CoreUI and AdminLTE themes

**Date:** 2026-11-23 · **Status:** draft for maintainer approval · **Repos:** django-crud-views-coreui,
django-crud-views-adminlte (same document in both).

## Intent

PR checks like Tabler's, so merges are not based on local runs only. CoreUI PR #5 and AdminLTE PR #1 were merged on local
`task test` and nox runs alone, because neither repository has a workflow.

## Goals

- Tests, Lint and Docs workflows on pull requests to `main` and pushes to `main`, as in django-crud-views-tabler.
- Coverage uploaded to Codecov from every Tests row, with a `codecov.yml` like Tabler's.
- Until django-crud-views 1.0.0rc1 is released, all three theme repos test against django-crud-views `main` (latest).
  Tabler and CoreUI already do; AdminLTE drops its pinned commit (`PIN` in `noxfile.py`).

## Non-goals

- Publish (PyPI), Render demo, Read the Docs: not PR checks; they stay a later follow-up.
- Branch protection or required checks: no repository protects `main` today (Tabler included); the checks inform.
- django-crud-views-extensions: it keeps testing against django-crud-views from PyPI (maintainer decision).
- A shared reusable workflow across the theme repos.

## Anti-goals

- A theme CI that installs django-crud-views from a pinned commit or from PyPI before 1.0.0rc1.
- A CI that differs from what `uvx nox` runs locally: the workflows only call nox sessions, ruff and mkdocs.

## Approaches

1. Port Tabler's three workflows into each repo, without Codecov. Self-contained; three near-identical copies.
2. **Chosen:** the same, plus Codecov (upload step and `codecov.yml`).
3. One shared reusable workflow in one repo, called by all themes. Dropped: each repo's CI would depend on another
   repo's file and version, which is harder to trace when a run breaks.

## Design

Per repo, copied from Tabler and adapted:

- `.github/requirements/ci.in` / `ci.txt`: the hash-locked tool list (nox, uv, ruff, build, packaging), regenerated with
  `uv pip compile --universal --generate-hashes --python-version 3.12`.
- `.github/workflows/tests.yml`: matrix Python 3.12–3.15 (`allow-prereleases`), `fail-fast: false`; per row the nox
  `tests-<py>(django=…)` and `examples-<py>(django=…)` sessions for the repo's Django versions (CoreUI 4.2, 5.2, 6.1;
  AdminLTE 6.0, 6.1; AdminLTE's 3.15 cells run and are logged as unsupported, as its noxfile does); then the
  `coverage-py*.xml` files go to `codecov/codecov-action` (same pinned SHA as Tabler) with `CODECOV_TOKEN` and a
  `py<version>` flag.
- `.github/workflows/lint.yml`: `ruff format --check .`, `ruff check .`, `nox -s package`.
- `.github/workflows/docs.yml`: `pip install --require-hashes -r docs/requirements.txt`, `mkdocs build --strict`.
- `codecov.yml`: Tabler's (advisory statuses, `after_n_builds: 4`, migrations ignored).
- `README.md`: Tests, Lint and Coverage badges at the top, as in Tabler's README.

AdminLTE only: `noxfile.py` installs `git+https://github.com/jacob-consulting/django-crud-views@main` like CoreUI and
Tabler, and `PIN` goes. The docs that describe the pin and the pin-bump step follow: the noxfile comment,
`pyproject.toml` comment, `CLAUDE.md`, `README.md`, `Taskfile.yaml` (`test:matrix`), `docs/development.md` and the
tracker's reference line. The plan's "Pin bump procedure" and the tracker's historical pin-bump section stay as history,
with a note that the pin is gone.

## Needs the maintainer

Codecov: enable both repositories on codecov.io and add each repository's upload token as the `CODECOV_TOKEN` secret.
Until then the upload step logs an error and the job still passes (`fail_ci_if_error` stays at its default, false).

## Left to the builder

Exact comment wording and the commit split.
