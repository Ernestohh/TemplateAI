# Hosting {{DOMAIN}} on the owner's server ({{SERVER_HOST}})

The site is static. `python scripts/build_site.py` assembles `site-dist/` with three parts:
- `/`: the game;
- `/trailer/`: the newest trailers;
- `/progress/`: the build log, with tokens, cost and the timeline.

## Server user

The scripts connect as `{{SERVER_SSH}}` (from `owner.json`: `server_user`@`server_host`) with an ssh key. Use a **non-root deploy user** with passwordless sudo for nginx, certbot and the web root; the scripts call `sudo -n` when the user is not root, so a missing rule fails fast instead of hanging on a password prompt. A minimal setup on the server (as root, once):

```bash
adduser --disabled-password deploy && mkdir -p ~deploy/.ssh && cp ~/.ssh/authorized_keys ~deploy/.ssh/ && chown -R deploy: ~deploy/.ssh
echo 'deploy ALL=(root) NOPASSWD: /usr/bin/mkdir, /usr/bin/tee, /usr/bin/tar, /usr/bin/rm, /usr/bin/mv, /usr/bin/install, /usr/bin/ln, /usr/sbin/nginx, /usr/bin/systemctl reload nginx, /usr/bin/certbot' > /etc/sudoers.d/deploy && chmod 440 /etc/sudoers.d/deploy && visudo -c
```

(Paths can differ per distribution: check them with `command -v`.) Logging in as root also works but is not recommended.

## Steps

1. **DNS (owner).** Add an **A record** `{{GAME_SLUG}}` pointing to the IP address of `{{SERVER_HOST}}` at the {{DNS_ZONE}} DNS provider. With Cloudflare, either the grey or the orange cloud works.
2. **Web server, once.** Run `DEPLOY_SSH={{SERVER_SSH}} bash scripts/server_setup.sh`. The script:
   - installs `deploy/nginx-site.conf` as `/etc/nginx/sites-available/{{DOMAIN}}` and symlinks it into `sites-enabled/`;
   - runs `nginx -t`, then reloads nginx;
   - when DNS already points at the server, runs `certbot --nginx -d {{DOMAIN}}` (HTTPS plus redirect).
3. **Upload, at every green gate.** Run `DEPLOY_SSH={{SERVER_SSH}} bash scripts/deploy_server.sh`. It builds, uploads to `{{DEPLOY_DIR}}` and swaps the folder in atomically. Then check that the live bundle name matches `dist/` (the script prints the command).

## Safety

The scripts touch only these:
- {{GAME_NAME}}'s own site file and symlink;
- `{{DEPLOY_DIR}}` (plus `.new`/`.old`);
- the `{{DOMAIN}}` certificate.

If `nginx -t` fails, the script removes {{GAME_NAME}}'s symlink again so the other sites keep running. Never edit other sites' configs, packages, users or firewall rules.

## Caching

- `sw.js` is never cached.
- HTML always revalidates.
- Hashed `/assets/` files are cached for a year.
- Music and fonts are cached for a week.
- Videos are cached for a day and are seekable.
