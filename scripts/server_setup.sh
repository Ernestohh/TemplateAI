#!/usr/bin/env bash
# One-time server setup for {{DOMAIN}} on the owner's server (nginx + certbot already installed there,
# as for the owner's other sites). Safe to re-run. Touches only:
#   /etc/nginx/sites-available/{{DOMAIN}}, its symlink in sites-enabled/, {{DEPLOY_DIR}},
#   and the certificate for {{DOMAIN}}.
# It never edits other sites. If `nginx -t` fails, it removes {{GAME_NAME}}'s symlink again and stops.
#   DEPLOY_SSH={{SERVER_SSH}} bash scripts/server_setup.sh
# HTTPS needs the DNS A record {{DOMAIN}} -> {{SERVER_IP}} first (the owner's DNS); without it the
# script sets up plain HTTP and says so.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${DEPLOY_SSH:?set DEPLOY_SSH, e.g. DEPLOY_SSH={{SERVER_SSH}}}"
DOMAIN={{DOMAIN}}
IP={{SERVER_IP}}
CONF=deploy/nginx-site.conf
[ -f "$CONF" ] || { echo "missing $CONF"; exit 1; }

echo "Uploading the nginx site file ..."
ssh "$DEPLOY_SSH" "cat > /tmp/{{GAME_SLUG}}-site.conf" < "$CONF"
ssh "$DEPLOY_SSH" "set -e
  mkdir -p {{DEPLOY_DIR}}
  [ -f {{DEPLOY_DIR}}/index.html ] || echo '<!doctype html><title>{{GAME_NAME}}</title><p>{{GAME_NAME}} is being built.</p>' > {{DEPLOY_DIR}}/index.html
  if [ -f /etc/nginx/sites-available/$DOMAIN ] && grep -q 'ssl_certificate' /etc/nginx/sites-available/$DOMAIN; then
    echo 'site file already has HTTPS (certbot edited it); leaving it unchanged'
  else
    install -m 644 /tmp/{{GAME_SLUG}}-site.conf /etc/nginx/sites-available/$DOMAIN
  fi
  ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/$DOMAIN
  if ! nginx -t; then
    rm -f /etc/nginx/sites-enabled/$DOMAIN
    echo 'nginx -t failed: removed the {{GAME_SLUG}} symlink again; other sites untouched'
    exit 1
  fi
  systemctl reload nginx
"
resolved=$(python -I -c "import socket,sys
try: print(socket.gethostbyname(sys.argv[1]))
except Exception: print('')" "$DOMAIN")
if [ "$resolved" = "$IP" ]; then
  echo "DNS ok ($DOMAIN -> $IP); requesting the certificate ..."
  ssh "$DEPLOY_SSH" "certbot --nginx -d $DOMAIN --non-interactive --agree-tos --redirect --keep-until-expiring --register-unsafely-without-email || certbot --nginx -d $DOMAIN --non-interactive --redirect --keep-until-expiring"
  echo "Done: https://$DOMAIN/"
else
  echo "DNS for $DOMAIN resolves to '${resolved:-nothing}', not $IP. HTTP site installed; HTTPS skipped."
  echo "Owner action: add an A record {{GAME_SLUG}} -> $IP at the {{DNS_ZONE}} DNS provider, then re-run this script."
fi
