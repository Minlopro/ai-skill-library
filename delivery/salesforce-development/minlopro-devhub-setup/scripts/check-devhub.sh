#!/bin/sh
# Read-only check that minlopro-prod is set up as a Dev Hub, and only as a Dev Hub.
# Usage: sh check-devhub.sh [alias] [login-url]   (default alias: minlopro-prod)
# login-url is Minlopro production's My Domain, e.g. https://<domain>.my.salesforce.com
ALIAS="${1:-minlopro-prod}"
LOGIN_URL="${2:-}"
FAIL=0
ok()   { printf '  OK    %s\n' "$1"; }
warn() { printf '  WARN  %s\n' "$1"; }
bad()  { printf '  FAIL  %s\n' "$1"; FAIL=1; }

echo "Minlopro Dev Hub check ($ALIAS)"

if ! command -v sf >/dev/null 2>&1; then bad "Salesforce CLI (sf) is not installed"; exit 1; fi
ok "Salesforce CLI $(sf --version 2>/dev/null | head -1 | cut -d' ' -f1)"

INFO=$(sf org display --target-org "$ALIAS" --json 2>/dev/null)
if ! printf '%s' "$INFO" | grep -q '"status": *0'; then
  bad "$ALIAS isn't logged in. Run: sf org login web --alias $ALIAS --instance-url ${LOGIN_URL:-https://<domain>.my.salesforce.com} --set-default-dev-hub"
  exit 1
fi
URL=$(printf '%s' "$INFO" | sed -n 's/.*"instanceUrl": *"\([^"]*\)".*/\1/p' | head -1)
ok "Logged in to $ALIAS ($URL)"
if [ -n "$LOGIN_URL" ]; then
  case "$URL" in "${LOGIN_URL%/}"*) ok "Matches the Minlopro production domain you gave";; *) bad "$ALIAS points at $URL, not $LOGIN_URL. Log in again with the right domain.";; esac
else warn "Pass Minlopro production's login URL as the second argument to confirm $ALIAS is the right org"; fi

# ScratchOrgInfo only exists in a Dev Hub org, and reading it needs the scratch-org permission.
if sf data query --target-org "$ALIAS" --query "SELECT COUNT() FROM ScratchOrgInfo" --json >/dev/null 2>&1; then ok "$ALIAS is a Dev Hub you can create scratch orgs from"; else bad "$ALIAS isn't working as a Dev Hub for you: either it isn't one, or you lack the 'Create and Delete Scratch Orgs' permission (ask a Proto admin)"; fi

HUB=$(sf config get target-dev-hub --json 2>/dev/null | sed -n 's/.*"value": *"\([^"]*\)".*/\1/p' | head -1)
if [ "$HUB" = "$ALIAS" ]; then ok "Default Dev Hub is $ALIAS"; else warn "Default Dev Hub is '${HUB:-not set}'. Pass --target-dev-hub $ALIAS, or run: sf config set target-dev-hub $ALIAS --global"; fi

TARGET=$(sf config get target-org --json 2>/dev/null | sed -n 's/.*"value": *"\([^"]*\)".*/\1/p' | head -1)
if [ "$TARGET" = "$ALIAS" ]; then bad "$ALIAS is your default TARGET org: deploy and data commands would hit Minlopro production. Run: sf config unset target-org --global"; else ok "$ALIAS is not your default target org"; fi

LIMITS=$(sf org list limits --target-org "$ALIAS" --json 2>/dev/null)
for N in ActiveScratchOrgs DailyScratchOrgs; do
  ROW=$(printf '%s' "$LIMITS" | tr -d '\n' | sed 's/},/}\n/g' | grep "\"name\": *\"$N\"")
  MAX=$(printf '%s' "$ROW" | sed -n 's/.*"max": *\([0-9]*\).*/\1/p'); REM=$(printf '%s' "$ROW" | sed -n 's/.*"remaining": *\([0-9]*\).*/\1/p')
  if [ -n "$MAX" ]; then
    if [ "${REM:-0}" -lt 5 ]; then warn "$N: $REM of $MAX left for the firm. Delete orgs you're done with."; else ok "$N: $REM of $MAX left for the firm"; fi
  else warn "Couldn't read $N (you may lack the scratch-org permission)"; fi
done

echo
if [ "$FAIL" -eq 0 ]; then echo "Ready. Create a scratch org with --target-dev-hub $ALIAS; never use $ALIAS as --target-org."; else echo "Fix the FAIL lines above, then run this again."; fi
exit $FAIL
