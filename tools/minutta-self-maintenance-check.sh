#!/usr/bin/env bash
set -u

usage() {
  cat <<'USAGE'
Usage: tools/minutta-self-maintenance-check.sh [--repo PATH]

Print metadata-only readiness information for the Minutta RP/PR workflow.

Options:
  --repo PATH  Repository checkout to inspect. Defaults to the current directory.
  --help       Show this help text.
USAGE
}

repo_path="."

while [ "$#" -gt 0 ]; do
  case "$1" in
    --help)
      usage
      exit 0
      ;;
    --repo)
      if [ "$#" -lt 2 ]; then
        printf 'error: --repo requires a path\n' >&2
        exit 2
      fi
      repo_path="$2"
      shift 2
      ;;
    *)
      printf 'error: unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ ! -d "$repo_path" ]; then
  printf 'error: repository path is not a directory\n' >&2
  exit 2
fi

if command -v git >/dev/null 2>&1; then
  git_available="yes"
else
  git_available="no"
fi

if [ "$git_available" = "no" ]; then
  printf 'utc_timestamp=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  printf 'repository_path=%s\n' "$repo_path"
  printf 'branch=unknown\n'
  printf 'status=unknown\n'
  printf 'git_available=no\n'
  printf 'gh_auth_present=no\n'
  printf 'codex_available=%s\n' "$(command -v codex >/dev/null 2>&1 && printf yes || printf no)"
  exit 1
fi

if ! repo_root="$(git -C "$repo_path" rev-parse --show-toplevel 2>/dev/null)"; then
  printf 'error: repository path is not inside a git checkout\n' >&2
  exit 1
fi

if branch="$(git -C "$repo_root" branch --show-current 2>/dev/null)" && [ -n "$branch" ]; then
  current_branch="$branch"
else
  current_branch="detached"
fi

if [ -n "$(git -C "$repo_root" status --porcelain 2>/dev/null)" ]; then
  clean_status="dirty"
else
  clean_status="clean"
fi

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  gh_auth_present="yes"
else
  gh_auth_present="no"
fi

if command -v codex >/dev/null 2>&1; then
  codex_available="yes"
else
  codex_available="no"
fi

printf 'utc_timestamp=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
printf 'repository_path=%s\n' "$repo_root"
printf 'branch=%s\n' "$current_branch"
printf 'status=%s\n' "$clean_status"
printf 'git_available=%s\n' "$git_available"
printf 'gh_auth_present=%s\n' "$gh_auth_present"
printf 'codex_available=%s\n' "$codex_available"
