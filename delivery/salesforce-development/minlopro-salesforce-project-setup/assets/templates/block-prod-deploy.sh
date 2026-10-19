#!/usr/bin/env bash
# Production-deploy GATE for the acme-prod org  (PreToolUse hook, matcher: Bash).
#
# Softened from the original hard block: an agent CAN now run a prod promote, but
# only through an explicit, documented gate.
#
#   * Anything that is NOT a real prod deploy/delete (incl. --dry-run) -> pass through.
#   * A real prod deploy/delete -> the hook checks the release preconditions:
#       1. an explicit --manifest / --metadata on the command
#          (promote a reviewed component set, not a blanket source-dir push);
#       2. deployment documentation  (docs/deployment/deployment-strategy.md);
#       3. a COMPLETED rollback strategy in that doc
#          (the "## Rollback" section is filled in, not the skeleton TODO).
#     - If any precondition is MISSING            -> "deny", saying exactly what to add.
#     - If ALL preconditions are satisfied        -> "ask", which forces the human to
#                                                    explicitly approve the promote.
#
# Fails CLOSED. The nuanced ask/deny decisions are emitted as JSON, which needs jq;
# if jq is absent the hook degrades to the original hard block (exit 2) rather than
# risk emitting malformed JSON that a permission engine might silently ignore.
# Known gaps (unchanged): default-org deploys, anonymous Apex, and MCP tool calls do
# not pass through this Bash hook. Keep the sandbox as the default org.

set -uo pipefail

PROD_ALIAS="acme-prod"                                   # slug-substituted at scaffold time
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
DEPLOY_DOC="$PROJECT_DIR/docs/deployment/deployment-strategy.md"

input=$(cat)

# --- No jq: degrade to the original hard block (still fail-closed) -------------
if ! command -v jq >/dev/null 2>&1; then
  if printf '%s' "$input" | grep -q "$PROD_ALIAS" \
     && printf '%s' "$input" | grep -Eq "deploy|delete" \
     && ! printf '%s' "$input" | grep -q -- "--dry-run"; then
    echo "BLOCKED: prod promote (jq not installed, approval gate degraded to hard block). Install jq to enable the approval gate; meanwhile a human runs the promote." >&2
    exit 2
  fi
  exit 0
fi

cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""')

# --- Gate only real prod deploys/deletes; everything else passes through -------
# NB: we deliberately do NOT emit permissionDecision:"allow" on the pass-through
# path -- that would auto-approve every Bash command and bypass normal prompts.
if ! printf '%s' "$cmd" | grep -q "$PROD_ALIAS" \
   || ! printf '%s' "$cmd" | grep -Eq "deploy|delete" \
   || printf '%s' "$cmd" | grep -q -- "--dry-run"; then
  exit 0
fi

emit() {  # $1 = allow|deny|ask   $2 = reason
  jq -nc --arg d "$1" --arg r "$2" \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:$d,permissionDecisionReason:$r}}'
}

# --- Check the release preconditions ------------------------------------------
missing=""
add() { missing="${missing}
  - $1"; }

printf '%s' "$cmd" | grep -Eq -- "--manifest|--metadata" \
  || add "an explicit --manifest (or --metadata): promote a reviewed component set, not a blanket source-dir push"

if [ ! -s "$DEPLOY_DOC" ]; then
  add "deployment documentation at docs/deployment/deployment-strategy.md"
else
  rollback=$(awk 'tolower($0) ~ /^## *rollback/{f=1;next} /^## /{f=0} f' "$DEPLOY_DOC")
  if [ -z "$(printf '%s' "$rollback" | tr -d '[:space:]')" ] \
     || printf '%s' "$rollback" | grep -Eiq "todo|tbd|<fill"; then
    add "a completed Rollback strategy in deployment-strategy.md (the ## Rollback section is empty or still the skeleton TODO)"
  fi
fi

# --- Decide -------------------------------------------------------------------
if [ -n "$missing" ]; then
  emit deny "Production promote to ${PROD_ALIAS} is not ready. Add the following first, then re-run:${missing}"
  exit 0
fi

emit ask "Production deploy to ${PROD_ALIAS}. Preconditions met: explicit manifest, deployment doc, and a documented rollback strategy. This is a REAL promote to prod -- approve only with the named release owner's explicit sign-off. If you are not that person, or anything is uncertain, reject."
exit 0
