# Development

## Layout of the repository

| Path | What |
|---|---|
| `src/crud_views_coreui/`, `src/django_coreui/` | the two packages of the distribution |
| `tests/crispy_coreui/`, `tests/crud_views_coreui/`, `tests/django_coreui/` | package tests, each with its own settings |
| `example/` | the Acme Roasters demo project and its tests |
| `docs/` | this documentation |
| `dev/` | maintainer notes, not published: the hand edits of the crispy pack |
| `superpowers/` | design specs, implementation plans and the upstream tracker (`superpowers/notes/upstream-tracker.md` in the GitHub repository jacob-consulting/django-crud-views-coreui; maintainer notes, not on this site) |
| `scripts/` | `vendor_templates.py` (crispy pack), `vendor_icons.py` (icons), `check_dist.py`, `check_release_floor.py` |

## Local setup

The theme tracks django-crud-views features that may not be released yet. Locally, django-crud-views and
django-crud-views-extensions are installed from sibling checkouts (`[tool.uv.sources]` in `pyproject.toml`):

```shell
git clone https://github.com/jacob-consulting/django-crud-views.git
git clone https://github.com/jacob-consulting/django-crud-views-extensions.git
git clone https://github.com/jacob-consulting/django-crud-views-coreui.git
cd django-crud-views-coreui
task up      # uv sync --extra examples --extra test --extra dev, migrate, superuser admin/admin, seed, runserver
```

Without [Task](https://taskfile.dev):

```shell
uv sync --extra examples --extra test --extra dev
uv run python example/manage.py migrate
uv run python example/manage.py cv_manage_group
uv run python example/manage.py seed_demo            # accounts alex, sam, kim (password demo)
uv run python example/manage.py seed_demo_showcase   # not idempotent: run once
uv run python example/manage.py runserver
```

Run `unset VIRTUAL_ENV` before `uv` commands if your shell sets one.

## Tests

```shell
task test          # every suite against the sibling checkouts, plus the system check
task test:matrix   # the nox matrix, as a CI matrix would run it
```

`task test` runs the three package suites (each with its own `--ds` settings module), the demo's tests from `example/`
and `manage.py check --fail-level WARNING`. The nox sessions (`noxfile.py`) build and install the distribution, so a
packaging mistake fails the tests:

- `tests-<python>(django='<version>')`: the three package suites, with coverage;
- `examples-<python>(django='<version>')`: the demo's tests and its system check;
- `package`: builds wheel and sdist and runs `scripts/check_dist.py`;
- `docs`: `mkdocs build --strict`.

```shell
uvx nox -s docs    # the documentation, strict
```

The matrix is Python 3.12-3.15 x Django 4.2, 5.2, 6.1 (Django 4.2 only on Python 3.12 and 3.13). Until
django-crud-views 1.0.0rc1 is on PyPI, nox installs django-crud-views from its GitHub `main` (`CRUD_VIEWS` in
`noxfile.py`).

Lint with ruff:

```shell
uv run ruff format . && uv run ruff check .
```

## Guards against upstream drift

The theme copies no upstream template; it uses upstream's hooks. Tests fail when upstream adds something those hooks
do not cover:

- a scan of the installed upstream templates and scripts fails on any that hard-codes `data-bs-` instead of the
  registered prefix, and every test app page (full and as a modal partial) must render without `data-bs-`;
- the CSS tests parse upstream's CSS (and the typeahead skins) and fail on a `--cv-*` token the theme does not set.

See [Theme internals](theme_internals.md).

## The crispy pack

`scripts/vendor_templates.py` copies the templates from the installed crispy-bootstrap5 into
`src/django_coreui/templates/crispy_coreui/`, rewriting `bootstrap5/` includes and `data-bs-` attributes. Two templates
are hand-edited and are not overwritten without `--force`. `django_coreui/crispy/vendored.py:CRISPY_BOOTSTRAP5_VERSION`
is the release the templates come from; the installed crispy-bootstrap5 must be one of `CRISPY_BOOTSTRAP5_COMPATIBLE`
(2026.3, the newest on Django 4.2, and 2026.9). nox pins the right one per Django version, and
`tests/crispy_coreui/test_pack_parity.py` compares the templates.

## Vendoring icons

```shell
python scripts/vendor_icons.py cil-rocket
```

See [Icons](icons.md).

## Releasing

1. Once django-crud-views 1.0.0rc1 is on PyPI: remove `CRUD_VIEWS` from `noxfile.py`, raise the floor in
   `pyproject.toml` to `django-crud-views (>=1.0.0rc1)`.
2. Update `CHANGELOG.md`.
3. The first release is the version already in the files: `git tag v0.1.0`. Later ones:
   `uv run bump-my-version bump patch` (or `minor`/`major`), which updates `pyproject.toml`, both `__init__.py`,
   `README.md` and `docs/index.md`, commits and tags `v<version>`.

`scripts/check_release_floor.py` refuses a release while the django-crud-views floor is below 1.0.0rc1. CI workflows,
Read the Docs and a hosted demo are not set up yet.
