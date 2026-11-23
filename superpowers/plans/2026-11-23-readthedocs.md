# Read the Docs Pipeline (CoreUI, AdminLTE) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the existing docs of django-crud-views-coreui and django-crud-views-adminlte on Read the Docs, with
pull-request preview builds, configured like django-crud-views-tabler.

**Architecture:** Read the Docs projects created through API v3 (connected through the Read the Docs GitHub App),
plus Tabler's `.readthedocs.yaml` and README badge in each repo.

**Tech Stack:** Read the Docs API v3, mkdocs (readthedocs theme), GitHub.

**Spec:** `superpowers/specs/2026-11-23-readthedocs-design.md` (same file in both repos).

## Global Constraints

- Project settings as `django-crud-views-tabler`: public, language `en`, programming language `words`, default branch
  `main`, default version `latest`, GitHub App remote repository, pull-request builds on.
- Slugs and URLs: `django-crud-views-coreui`, `django-crud-views-adminlte`;
  `https://django-crud-views-<theme>.readthedocs.io/en/latest/`.
- The API token lives only in the session scratchpad file `rtd-token` (mode 600); never in a repo file, commit, PR or
  echoed output; the file is deleted at the end (Task 3).

## Review Focus

- The RTD GitHub App does not list a repo yet (sync lag): Task 1 stops and reports instead of importing a
  webhook-only project.
- A project created without the remote-repository link: no PR checks. Task 1 compares its `repository` / remote
  repository with Tabler's before the PRs.
- The first build fails on RTD while GitHub's `docs.yml` passes (different Python, RTD's mkdocs handling): the PR's RTD
  check must be green before merge (Task 2).
- `latest` not built after the merge: Task 3 checks the URL answers 200.

---

### Task 1: Create both Read the Docs projects

- [ ] **Step 1:** `GET /api/v3/remote/repositories/?name=django-crud-views-<theme>` lists the repo with
  `vcs_provider: githubapp` for both themes; otherwise stop and report.
- [ ] **Step 2:** `POST /api/v3/projects/` with `name`, `repository: {url: https://github.com/jacob-consulting/<repo>, type: git}`,
  `language: en`, `programming_language: words`, `homepage: <GitHub URL>`.
- [ ] **Step 3:** `PATCH /api/v3/projects/<slug>/` with `default_branch: main`, `external_builds_enabled: true`,
  `privacy_level: public`.
- [ ] **Step 4: Verify** with `GET`: settings equal the Global Constraints; the remote-repositories listing now names the
  project for each repo, as it does for Tabler.

### Task 2: Repo changes and PRs (each repo, branch `docs/readthedocs`)

**Files:** Create `.readthedocs.yaml` (copy of Tabler's); Modify `README.md` (Docs badge after Coverage; CoreUI: the
"not published yet" Documentation line becomes the plain link); Add the spec and this plan.

- [ ] **Step 1:** Make the changes; `grep -n tabler .readthedocs.yaml README.md` → no output.
- [ ] **Step 2:** Commit `docs: publish on Read the Docs (.readthedocs.yaml, badge)`, push, open the PR.
- [ ] **Step 3: Verify:** the PR shows `docs/readthedocs.org:django-crud-views-<theme>` passing, its preview URL answers
  200, and Tests/Lint/Docs pass.

### Task 3: Merge and confirm

- [ ] **Step 1:** Merge both PRs when green (merge commit, as before); sync the local `main`.
- [ ] **Step 2: Verify:** the `latest` build from `main` succeeds and `https://django-crud-views-<theme>.readthedocs.io/en/latest/`
  answers 200 for both.
- [ ] **Step 3:** Delete the scratchpad token file; remind the maintainer to rotate the token.
