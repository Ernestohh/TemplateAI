#!/usr/bin/env bash
# One-time server setup for {{DOMAIN}} on the owner's server {{SERVER_HOST}} (nginx and certbot already
# installed there). Safe to re-run. Touches only:
#   /etc/nginx/sites-available/{{DOMAIN}}, its symlink in sites-enabled/, {{DEPLOY_DIR}},
#   and the certificate for {{DOMAIN}}.
# It never edits other sites. If `nginx -t` fails, it removes {{GAME_NAME}}'s symlink again and stops.
#   DEPLOY_SSH={{SERVER_SSH}} bash scripts/server_setup.sh
# The ssh user should be a non-root deploy user with passwordless sudo for nginx, certbot and the web root
# (deploy/README.md); the script uses `sudo -n` when the user is not root. root also works.
# HTTPS needs the DNS A record {{DOMAIN}} -> the IP of {{SERVER_HOST}} first (the owner's DNS); without it the
# script sets up plain HTTP and says so.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${DEPLOY_SSH:?set DEPLOY_SSH, e.g. DEPLOY_SSH={{SERVER_SSH}}}"
DOMAIN={{DOMAIN}}
HOST={{SERVER_HOST}}
CONF=deploy/nginx-site.conf
[ -f "$CONF" ] || { echo "missing $CONF"; exit 1; }

echo "Uploading the nginx site file ..."
ssh "$DEPLOY_SSH" "cat > /tmp/{{GAME_SLUG}}-site.conf" < "$CONF"
ssh "$DEPLOY_SSH" "set -e
  S=''; [ \"\$(id -u)\" = 0 ] || S='sudo -n'
  \$S mkdir -p {{DEPLOY_DIR}}
  [ -f {{DEPLOY_DIR}}/index.html ] || echo '<!doctype html><title>{{GAME_NAME}}</title><p>{{GAME_NAME}} is being built.</p>' | \$S tee {{DEPLOY_DIR}}/index.html >/dev/null
  if [ -f /etc/nginx/sites-available/$DOMAIN ] && grep -q 'ssl_certificate' /etc/nginx/sites-available/$DOMAIN; then
    echo 'site file already has HTTPS (certbot edited it); leaving it unchanged'
  else
    \$S install -m 644 /tmp/{{GAME_SLUG}}-site.conf /etc/nginx/sites-available/$DOMAIN
  fi
  \$S ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/$DOMAIN
  if ! \$S nginx -t; then
    \$S rm -f /etc/nginx/sites-enabled/$DOMAIN
    echo 'nginx -t failed: removed the {{GAME_SLUG}} symlink again; other sites untouched'
    exit 1
  fi
  \$S systemctl reload nginx
"
resolve() { python -I -c "import socket,sys
try: print(socket.gethostbyname(sys.argv[1]))
except Exception: print('')" "$1"; }
resolved=$(resolve "$DOMAIN")
IP=$(resolve "$HOST")
if [ -n "$resolved" ] && [ "$resolved" = "$IP" ]; then
  echo "DNS ok ($DOMAIN -> $IP); requesting the certificate ..."
  ssh "$DEPLOY_SSH" "S=''; [ \"\$(id -u)\" = 0 ] || S='sudo -n'
    \$S certbot --nginx -d $DOMAIN --non-interactive --agree-tos --redirect --keep-until-expiring --register-unsafely-without-email || \$S certbot --nginx -d $DOMAIN --non-interactive --redirect --keep-until-expiring"
  echo "Done: https://$DOMAIN/"
else
  echo "DNS for $DOMAIN resolves to '${resolved:-nothing}', not ${IP:-the IP of $HOST}. HTTP site installed; HTTPS skipped."
  echo "Owner action: add an A record {{GAME_SLUG}} -> ${IP:-the IP of $HOST} at the {{DNS_ZONE}} DNS provider, then re-run this script."
fi
