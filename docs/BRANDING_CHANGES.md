# Branding Changes Summary

Updated site branding to "DeVul" and linked to your GitHub repository.

- Site name: DeVul
- Primary link: https://github.com/jasstej/DeVulDecompiler
- Templates updated: `templates/explorer/index.html`, `about.html`, `queue.html`, `faq.html`, `404.html`, `500.html`
- Manifest updated: `static/site.webmanifest`
- Theme colors updated: `static/css/style.css`
- Removed external analytics script from templates
- README updated to reference your repo

Optional cleanups:
- Remove unused images: `static/img/dogbolt.png`, `static/img/dogbolt-small.png`
- Rebuild static files after changes:
```zsh
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec explorer python manage.py collectstatic --noinput
```
