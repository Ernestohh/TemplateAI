#!/usr/bin/env bash
# Upload the website (game at /, trailers at /trailer/, build log at /progress/) to the owner's server ({{SERVER_HOST}}).
#   DEPLOY_SSH={{SERVER_SSH}} bash scripts/deploy_server.sh
# Optional: DEPLOY_DIR (default {{DEPLOY_DIR}}). Needs ssh access (key) to the server.
# One-time server setup (nginx site + HTTPS): bash scripts/server_setup.sh (see deploy/README.md).
# Touches only $DEPLOY_DIR (and $DEPLOY_DIR.new / $DEPLOY_DIR.old) on the server.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${DEPLOY_SSH:?set DEPLOY_SSH, e.g. DEPLOY_SSH={{SERVER_SSH}}}"
DIR="${DEPLOY_DIR:-{{DEPLOY_DIR}}}"
case "$DIR" in {{DEPLOY_DIR}}*) ;; *) echo "refusing: DEPLOY_DIR must be under {{DEPLOY_DIR}}"; exit 1 ;; esac
npm run build
python scripts/build_site.py
echo "Uploading site-dist/ to $DEPLOY_SSH:$DIR ..."
# Upload to a fresh folder, then swap it in, so visitors never see a half-copied site.
# A non-root deploy user needs passwordless sudo (deploy/README.md); `sudo -n` fails fast instead of prompting.
tar -C site-dist -czf - . | ssh "$DEPLOY_SSH" "set -e; S=''; [ \"\$(id -u)\" = 0 ] || S='sudo -n'; \$S mkdir -p '$DIR.new' && \$S tar -xzf - -C '$DIR.new' && \$S rm -rf '$DIR.old' && { [ -d '$DIR' ] && \$S mv '$DIR' '$DIR.old' || true; } && \$S mv '$DIR.new' '$DIR'"
local_js=$(ls dist/assets/index-*.js 2>/dev/null | head -1 | xargs -r basename)
echo "Done: https://{{DOMAIN}}/  (local bundle: ${local_js:-unknown})"
echo "Verify: curl -s https://{{DOMAIN}}/ | grep -o 'index-[A-Za-z0-9_-]*\.js' should print ${local_js:-the same name}"
