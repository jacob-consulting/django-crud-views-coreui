# CI PR Checks (CoreUI, AdminLTE) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tests, Lint and Docs workflows (with Codecov) in django-crud-views-coreui and django-crud-views-adminlte, and
AdminLTE testing against django-crud-views `main` instead of a pinned commit.

**Architecture:** Copy django-crud-views-tabler's `tests.yml`, `lint.yml`, `docs.yml`, `.github/requirements/ci.*` and
`codecov.yml` into each repo; the workflows only call each repo's own nox sessions, ruff and mkdocs. AdminLTE's
noxfile switches its `CRUD_VIEWS` requirement to `@main` and loses `PIN`.

**Tech Stack:** GitHub Actions, nox (uv backend), ruff, mkdocs, codecov-action.

**Spec:** `superpowers/specs/2026-11-23-ci-pr-checks-design.md` (same file in both repos).

## Global Constraints

- Triggers: `pull_request` to `main` and `push` to `main` (Tests, Lint); Docs as Tabler's `docs.yml` (`pull_request` to
  `main`, tags `v*`).
- Python matrix `["3.12", "3.13", "3.14", "3.15"]`, `allow-prereleases: true`, `fail-fast: false`.
- Django sessions: CoreUI `4.2`, `5.2`, `6.1`; AdminLTE `6.0`, `6.1`.
- Theme CI installs django-crud-views from `git+https://github.com/jacob-consulting/django-crud-views@main` until
  1.0.0rc1; never a pinned commit, never PyPI.
- Action versions exactly as Tabler: `actions/checkout@v7`, `actions/setup-python@v7`,
  `codecov/codecov-action@303a32d7a59b442fa8d48b6a1cc6825c09c847a5 # v7.1.1`.
- Tool installs only via `pip install --require-hashes --only-binary :all: -r <file>`.
- No publish, demo, Read the Docs or branch-protection changes; django-crud-views-extensions untouched.

## Review Focus

- A Tests row whose sessions produce no `coverage-py*.xml` (e.g. a renamed nox session): `ls` must not be the reason a
  row fails silently-empty; expect the row to fail visibly. Checked by the first PR run (Task 4).
- Codecov without `CODECOV_TOKEN`: upload step reports an error, job stays green. Checked in Task 4's PR run.
- AdminLTE's 3.15 cells: they run (logged unsupported) and must not be filtered out of the workflow matrix.
- A copied workflow still naming `tabler` (badge URL, session names): grep check in Tasks 1 and 3.
- Stale "pinned commit" wording left in AdminLTE docs after the unpin: grep check in Task 2.

---

### Task 1: CoreUI CI files

**Files (repo django-crud-views-coreui, branch `ci/pr-checks`):**
- Create: `.github/requirements/ci.in`, `.github/requirements/ci.txt` (copies of Tabler's)
- Create: `.github/workflows/tests.yml`, `lint.yml`, `docs.yml` (copies of Tabler's)
- Create: `codecov.yml` (copy of Tabler's)
- Modify: `README.md` (badges under the title)
- Add: this plan and the spec

**Interfaces:**
- Produces: workflow files named `tests.yml`, `lint.yml`, `docs.yml` (badge URLs depend on these names).

- [ ] **Step 1:** Copy the files above from `../django-crud-views-tabler`. CoreUI's nox session names and Django list equal
  Tabler's, so `tests.yml` needs no session edits.
- [ ] **Step 2:** README: insert Tests, Lint and Coverage badges after the `# django-crud-views-coreui` line, Tabler's
  markup with `tabler` → `coreui` (no Docs badge: Read the Docs is out of scope).
- [ ] **Step 3: Verify.** `grep -rn tabler .github codecov.yml README.md` → no output;
  `uvx nox -l | grep -c "tests-3.1[2-5](django='\(4.2\|5.2\|6.1\)')"` → `12`; YAML parses:
  `python3 -c "import yaml,glob;[yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml')]"`.
- [ ] **Step 4: Commit** `ci: tests, lint and docs workflows with Codecov, as in the Tabler theme`.

### Task 2: AdminLTE tests django-crud-views `main`

**Files (repo django-crud-views-adminlte, branch `ci/pr-checks`):**
- Modify: `noxfile.py:12-17,55` (drop `PIN`; `CRUD_VIEWS` = CoreUI's two-line `@main` form; comments say `main`)
- Modify: `pyproject.toml:70`, `CLAUDE.md:17-20`, `README.md:55`, `Taskfile.yaml:85`, `docs/development.md:64`
- Modify: `superpowers/notes/upstream-tracker.md` (reference line: tests against `main`; note under "Pin bump to
  `95e3fb33`" that the pin is gone since 2026-11-23)
- Modify: `superpowers/plans/2026-11-21-adminlte-theme.md` ("Pin bump procedure": one-line note that it is retired)

- [ ] **Step 1:** Edit the noxfile and the docs above.
- [ ] **Step 2: Verify.** `grep -rn "PIN\b\|pinned" noxfile.py pyproject.toml CLAUDE.md README.md Taskfile.yaml docs/`
  → no output; `uvx nox -s "tests-3.12(django='6.0')"` → passes and its log shows the `@main` git install.
- [ ] **Step 3: Commit** `build: test against django-crud-views main instead of a pinned commit`.

### Task 3: AdminLTE CI files

**Files:** as Task 1, in django-crud-views-adminlte.

**Interfaces:**
- Consumes: Task 2's noxfile (sessions `tests-<py>(django='6.0'|'6.1')`, `examples-…`, `package`).

- [ ] **Step 1:** Copy as Task 1. In `tests.yml`, both nox steps list `django='6.0'` and `django='6.1'` (not 4.2/5.2/6.1).
- [ ] **Step 2:** README badges as Task 1 with `adminlte`.
- [ ] **Step 3: Verify** as Task 1 Step 3, with count `8` for `(6.0|6.1)` and no `tabler`.
- [ ] **Step 4: Commit** as Task 1.

### Task 4: PRs and first runs

- [ ] **Step 1:** Push both branches (HTTPS remote URL), open a PR in each against `main`.
- [ ] **Step 2: Verify** with `gh pr checks <n> --watch`: Tests (4 rows), Lint and Docs pass in both repos; the Codecov
  step's log shows the missing-token error without failing the job.
- [ ] **Step 3:** Report the PR links and results; merging waits for the maintainer, as do the Codecov repositories and
  `CODECOV_TOKEN` secrets.
