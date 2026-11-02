#!/usr/bin/env bash
# ============================================================
#  commit_journal.sh - persist the trade journal to the repo.
#
#  * Commits journal/*.csv, journal_state.json and a daily
#    .heartbeat file (the heartbeat doubles as repo activity
#    so GitHub never auto-disables the schedule after 60 days).
#  * Handles the rare race where two runs pushed in sequence
#    by rebasing on top of the remote before pushing.
#  * No-op (clean exit) when nothing changed.
# ============================================================
set -e

BRANCH="${GITHUB_REF_NAME:-main}"

git config user.name  "scanner-bot"
git config user.email "actions@users.noreply.github.com"

# daily heartbeat: changes once per day -> one keepalive commit/day
mkdir -p journal
date -u +%F > journal/.heartbeat

git add journal/

if git diff --cached --quiet; then
    echo "No journal changes to commit."
    exit 0
fi

git commit -m "journal: auto update [skip ci]"

ok=0
for i in 1 2 3; do
    git rebase --abort >/dev/null 2>&1 || true
    if git pull --rebase --autostash origin "$BRANCH" && git push origin "HEAD:$BRANCH"; then
        ok=1
        echo "Journal pushed to $BRANCH."
        break
    fi
    echo "Push attempt $i failed (remote moved); retrying after rebase..."
    sleep 4
done

if [ "$ok" -ne 1 ]; then
    echo "::warning::Journal could not be pushed after 3 attempts. " \
         "It will be re-committed by the next run."
    exit 1
fi
