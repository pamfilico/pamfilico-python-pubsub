#!/bin/bash
# deploy.sh - Automated deployment script for pamfilico-python-pubsub
# Usage: ./deploy.sh -m "fix: bug fix"  |  ./deploy.sh -m "feat: new" -i minor
set -e

INCREMENT="patch"
COMMIT_MESSAGE=""
SKIP_COMMIT=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case $1 in
    -m|--message) COMMIT_MESSAGE="$2"; shift 2 ;;
    -i|--increment) INCREMENT="$2"; shift 2 ;;
    -s|--skip-commit) SKIP_COMMIT=true; shift ;;
    -d|--dry-run) DRY_RUN=true; shift ;;
    *) echo "Unknown: $1"; exit 1 ;;
  esac
done

[ ! -f pyproject.toml ] && { echo "Run from package root."; exit 1; }
[ ! -e .git ] && { echo "Not a git repo."; exit 1; }

echo "=================================="
echo "  Pamfilico Python Pubsub Deploy"
echo "=================================="

if [ "$SKIP_COMMIT" = false ] && ! git diff-index --quiet HEAD -- 2>/dev/null; then
  [ -z "$COMMIT_MESSAGE" ] && { echo "Provide -m \"message\" or use -s"; exit 1; }
  git add -A
  git commit -m "$COMMIT_MESSAGE"
fi

CURRENT_VERSION=$(grep -m 1 '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
[ "$DRY_RUN" = true ] || poetry run cz bump --increment "$INCREMENT" --yes
NEW_VERSION=$(grep -m 1 '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')

[ "$DRY_RUN" = true ] || git push origin master --tags
echo "Done: $CURRENT_VERSION → $NEW_VERSION"
