# Toolchain install — admin vs no-admin branches

Phase 1 installs only what's missing. Detect the machine's capability FIRST, then
follow the matching branch. Check each tool with `command -v` before installing it.

## Detect which branch to use (macOS)
Run these non-interactively (no password prompt):

    command -v brew          # if present -> Admin/Homebrew branch
    id -Gn | grep -qw admin  # if present but no brew -> user COULD install Homebrew

Decision:
- `brew` already installed            -> Admin/Homebrew branch.
- No brew, user IS in `admin` group   -> tell the user; offer to install Homebrew
                                         (its installer will prompt for their
                                         password — they run that part), OR proceed
                                         no-admin. Default to asking.
- No brew, user NOT in `admin` group  -> No-admin branch (never sudo, never
                                         /usr/local).
- Windows                             -> use winget (see bottom).

Whichever branch installs the tools, everything after Phase 1 is identical.

---

## Admin / Homebrew branch (macOS/Linux)
    # Node 20+
    brew install node
    # GitHub CLI
    brew install gh
    # jq — REQUIRED by the prod-deploy guardrail hook (not preinstalled on macOS)
    brew install jq
    # Salesforce CLI
    npm install -g @salesforce/cli

## No-admin branch (managed Mac — home-dir installs only)
NEVER use sudo; NEVER write to /usr/local. Download with curl (not the browser) so
macOS doesn't quarantine bundled binaries.

    # --- Node via nvm (provides npx; no admin) ---
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
    #   reopen the terminal, then:
    nvm install --lts && node -v && npm -v && npx -v

    # --- Salesforce CLI: standalone tarball into ~/sf (bundles its own Node) ---
    mkdir -p ~/sf
    uname -m   # arm64 = Apple Silicon; x86_64 = Intel
    # Apple Silicon:
    curl -fsSL https://developer.salesforce.com/media/salesforce-cli/sf/channels/stable/sf-darwin-arm64.tar.xz -o ~/sf.tar.xz
    #   (Intel: swap the filename to sf-darwin-x64.tar.xz)
    tar xJf ~/sf.tar.xz -C ~/sf --strip-components 1
    echo 'export PATH="$HOME/sf/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
    sf --version && rm ~/sf.tar.xz

    # --- jq: single static binary into ~/.local/bin (REQUIRED by the guardrail hook) ---
    mkdir -p ~/.local/bin
    curl -fsSL https://github.com/jqlang/jq/releases/latest/download/jq-macos-arm64 -o ~/.local/bin/jq
    #   (Intel: jq-macos-amd64)
    chmod +x ~/.local/bin/jq && jq --version

    # --- GitHub CLI: binary into ~/.local/bin (no admin) ---
    mkdir -p ~/.local/bin
    #   resolve the latest macOS asset from the GitHub releases API and curl it
    #   (gh_*_macOS_arm64.zip for Apple Silicon, gh_*_macOS_amd64.zip for Intel):
    unzip ~/Downloads/gh_*_macOS_*.zip -d /tmp/gh
    cp /tmp/gh/gh_*/bin/gh ~/.local/bin/ && gh --version
    #   (Fallback if network policy blocks gh: create the repo in the browser and
    #    push over HTTPS with a Personal Access Token; skip `gh repo create`.)

---

## Common to BOTH branches (run after the CLIs are on PATH)
    # Salesforce CLI plugins
    sf plugins install sfdx-git-delta code-analyzer
    # Salesforce agent skills
    npx skills add forcedotcom/sf-skills

    # GitHub auth + git identity (browser flow — pause for the user)
    gh auth login          # GitHub.com -> HTTPS -> browser
    gh auth setup-git
    git config --global user.name  "<ask the user>"
    git config --global user.email "<ask the user>"

    # Salesforce org logins (one at a time; the user completes each MFA in browser)
    # Client work:
    sf org login web --instance-url https://test.salesforce.com  --alias acme-sandbox --set-default
    sf org login web --instance-url https://test.salesforce.com  --alias acme-uat
    sf org login web --instance-url https://login.salesforce.com --alias acme-prod   # NOT default
    #   (Demo path: a Developer Edition org / Dev Hub instead — ask which path first.)
    sf org list   # confirm the default is the sandbox

    # Chrome remote debugging (human-consent, one click): in Chrome (v144+) open
    # chrome://inspect/#remote-debugging, click Allow, use a dedicated test profile.

## Windows (PowerShell, native — no WSL)
    winget install OpenJS.NodeJS.LTS
    winget install GitHub.cli
    npm install -g @salesforce/cli
Then the same "Common to BOTH branches" steps. Install Git so Claude Code has a
real Bash shell; %USERPROFILE%\.local\bin must be on PATH.
