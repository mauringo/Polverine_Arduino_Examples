#!/usr/bin/env bash
# macOS (Bash 3.2+) and Linux. Requires Git and Python 3 on PATH.
# Uses normal Git authentication: SSH, credential helper, or VS Code terminal.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
case "$(uname -s)" in
    Darwin|Linux) ;;
    *) printf 'This script supports macOS and Linux.\n' >&2; exit 1;;
esac
for dependency in git python3; do
    command -v "$dependency" >/dev/null 2>&1 || {
        printf 'Missing dependency: %s. Install it and retry.\n' "$dependency" >&2
        exit 1
    }
done

usage() {
    cat <<'HELP'
Usage: ./publish.sh [main|bme690|bsec3|libraries] [--check|--commit-only]

No arguments: choose main project or libraries, then which library.
Works on macOS and Linux with Bash, Git and Python 3.
  libraries  Publish both BME690-Arduino-lib-unofficial and Bsec3-ArduinoLibrary-Unofficial.
  main       Publish the PlatformIO + Arduino project to its own origin.
  example    Alias for main.
  --check    Show status and check for forbidden files without changing anything.
  --commit-only  Stage and commit selected source changes, without pushing.

Existing commits are pushed. If there are edits, you choose a commit message.
ZIPs, Bosch binaries and generated Arduino libraries are excluded and audited.
HELP
}

target=""
check_only=false
commit_only=false
for argument in "$@"; do
    case "$argument" in
        --help|-h) usage; exit 0;;
        --check) check_only=true;;
        --commit-only) commit_only=true;;
        main|example|bme690|bsec3|libraries)
            if [[ -n "$target" ]]; then usage; exit 2; fi
            target="$argument";;
        *) usage; exit 2;;
    esac
done

if "$check_only" && "$commit_only"; then usage; exit 2; fi

if [[ -z "$target" ]]; then
    while true; do
        printf '\nWhat do you want to publish?\n  1) Main project (PlatformIO + Arduino)\n  2) Libraries\n  0) Cancel\n'
        read -r -p 'Choice [0-2]: ' choice
        case "$choice" in
            1) target=example; break;;
            2) target=libraries; break;;
            0) exit 0;;
            *) printf 'Please choose 0, 1, or 2.\n';;
        esac
    done
    if [[ "$target" == libraries ]]; then
        while true; do
            printf '\nWhich libraries?\n  1) BME690-Arduino-lib-unofficial\n  2) Bsec3-ArduinoLibrary-Unofficial\n  3) Both libraries\n  0) Cancel\n'
            read -r -p 'Choice [0-3]: ' choice
            case "$choice" in
                1) target=bme690; break;;
                2) target=bsec3; break;;
                3) break;;
                0) exit 0;;
                *) printf 'Please choose 0, 1, 2, or 3.\n';;
            esac
        done
    fi
fi
case "$target" in
    main) target=example;;
esac
case "$target" in
    libraries) targets=(bme690 bsec3);;
    bme690|bsec3|example) targets=("$target");;
esac

repo_for() {
    case "$1" in
        bme690) printf '%s/lib/BME690-Arduino-lib-unofficial' "$ROOT";;
        bsec3) printf '%s/lib/Bsec3-ArduinoLibrary-Unofficial' "$ROOT";;
        example) printf '%s' "$ROOT";;
    esac
}

for item in "${targets[@]}"; do
    python3 scripts/repos.py status "$item"
    python3 scripts/repos.py audit "$item"
    repo="$(repo_for "$item")"
    if git -C "$repo" rev-parse --verify HEAD >/dev/null 2>&1; then
        git -C "$repo" --no-pager diff HEAD --stat
    fi
done
if "$check_only"; then printf '\nChecks passed. Nothing changed or pushed.\n'; exit 0; fi

for item in "${targets[@]}"; do
    repo="$(repo_for "$item")"
    printf '\n--- Commit: %s ---\n' "$item"
    if [[ -n "$(git -C "$repo" status --porcelain --untracked-files=all)" ]]; then
        case "$item" in
            example) default_message='Update Polverine Arduino examples';;
            bme690) default_message='Update BME690-Arduino-lib-unofficial';;
            bsec3) default_message='Update Bsec3-ArduinoLibrary-Unofficial';;
        esac
        read -r -p "Commit message [$default_message]: " message
        message="${message:-$default_message}"
        if ! python3 scripts/repos.py commit "$item" -m "$message"; then
            printf 'Commit failed for %s. Nothing will be pushed.\n' "$item" >&2
            exit 1
        fi
        printf 'Committed changes in %s.\n' "$item"
    else
        printf 'No uncommitted source changes in %s; the existing commit is ready to push.\n' "$item"
    fi
    if git -C "$repo" rev-parse --verify HEAD >/dev/null 2>&1; then
        git -C "$repo" --no-pager log -1 --oneline
    fi
done
if "$commit_only"; then printf '\nCommit step complete. Nothing pushed.\n'; exit 0; fi

# A commit does not require a remote or GitHub authentication.
for item in "${targets[@]}"; do
    repo="$(repo_for "$item")"
    if ! git -C "$repo" remote get-url origin >/dev/null 2>&1; then
        printf '\n%s has no origin. Create an empty GitHub repository first.\n' "$item"
        read -r -p 'Paste its Git remote URL (blank stops before pushing): ' remote_url
        [[ -n "$remote_url" ]] || exit 1
        git -C "$repo" remote add origin "$remote_url"
    fi
    printf '\n%s → %s\n' "$item" "$(git -C "$repo" remote get-url origin)"
done

read -r -p 'Push the selected repositories to the origins shown above? [y/N] ' answer
case "$answer" in y|Y|yes|YES) ;; *) printf 'Local commits retained. Nothing pushed.\n'; exit 0;; esac
for item in "${targets[@]}"; do
    if ! python3 scripts/repos.py push "$item"; then
        printf '\nPush failed for %s. Check your Git authentication (SSH key, credential helper, or VS Code terminal sign-in) and complete any authentication prompt.\n' "$item" >&2
        printf 'Your local commits are retained. Retrying is safe; no force push is used.\n' >&2
        exit 1
    fi
    if [[ "$item" != example ]]; then
        read -r -p "Also publish an Arduino version tag for $item? [y/N] " release_answer
        case "$release_answer" in
            y|Y|yes|YES) python3 scripts/repos.py release "$item";;
        esac
    fi
done
printf '\nPublished successfully. ZIPs and Bosch binaries were excluded.\n'
if [[ "$target" != example && -n "$(git -C "$ROOT" status --porcelain --untracked-files=all)" ]]; then
    printf 'The main project has uncommitted changes (including updated library references).\n'
    printf 'Run ./publish.sh main to commit and publish the main project separately.\n'
fi
