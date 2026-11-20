# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

The distribution **django-crud-views-coreui** (repo `jacob-consulting/django-crud-views-coreui`): a CoreUI 5 (free)
sister of django-crud-views-tabler, ported from `../tabler-test`. Two packages under `src/`: `django_coreui` (page
shell, must not import `crud_views`) and `crud_views_coreui` (theme for django-crud-views). Supported: Python
3.12-3.15 x Django 4.2, 5.2, 6.1 (4.2 only on 3.12/3.13); local development runs Python 3.14.

`../django-crud-views` and `../django-crud-views-extensions` are editable path sources (read-only for this repo).
nox installs django-crud-views from GitHub `main` until 1.0.0rc1 is on PyPI (`scripts/check_release_floor.py`).

Design and plan: `superpowers/specs/`, `superpowers/plans/`; upstream tracker: `superpowers/notes/upstream-tracker.md`.
This file is a stub; later tasks extend it.

## Commands

```shell
unset VIRTUAL_ENV   # before uv commands, if the parent environment sets one
uv sync --extra examples --extra test --extra dev
uv run pytest -n auto tests/django_coreui --ds tests.django_coreui.settings
uv run ruff format . && uv run ruff check .
```
