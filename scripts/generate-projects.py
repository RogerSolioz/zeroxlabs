#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère les pages vitrine projet à partir de projets/projects.json."""
import json, os, html, re

ROOT = '/home/user/zeroxlabs'
data = json.load(open(os.path.join(ROOT, 'projets/projects.json'), encoding='utf-8'))

def esc(s): return html.escape(str(s), quote=True)

def hex_to_rgba(hx, a):
    hx = hx.lstrip('#')
    r, g, b = int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)
    return f"rgba({r},{g},{b},{a})"

ICON_BY_CATEGORY = {
    'App web': 'bi-window',
    'App mobile iOS': 'bi-phone',
    'Jeu / Expérience web': 'bi-controller',
    'Outil': 'bi-tools',
}
ICON_BY_SLUG = {
    'lotobooster': 'bi-suit-club-fill',
    'chillcards': 'bi-postcard-fill',
    'yearloop': 'bi-calendar-event',
    'the-age-of-bryan': 'bi-trophy-fill',
}
STATUS_ICON = {'En ligne': 'bi-broadcast', 'Bêta': 'bi-rocket-takeoff', 'Bientôt': 'bi-hourglass-split'}

def is_ready(p):
    return not str(p.get('category', '')).startswith('TODO')

def project_icon(p):
    return ICON_BY_SLUG.get(p['slug'], ICON_BY_CATEGORY.get(p['category'], 'bi-stars'))

def feature_items(features):
    out = []
    for f in features:
        out.append(f'''        <div class="col-md-6 col-lg-4">
          <div class="project-feature">
            <span class="pf-icon"><i class="bi bi-check2" aria-hidden="true"></i></span>
            <p class="mb-0">{esc(f)}</p>
          </div>
        </div>''')
    return '\n'.join(out)

def tech_chips(tech):
    if not tech: return ''
    chips = '\n'.join(f'        <span class="tech-chip">{esc(t)}</span>' for t in tech if not str(t).startswith('TODO'))
    if not chips.strip(): return ''
    return f'''
  <section class="project-section alt" aria-labelledby="stack-heading">
    <div class="container text-center">
      <h2 id="stack-heading" class="fw-bold mb-4">Sous le capot</h2>
      <div class="d-flex flex-wrap justify-content-center gap-2">
{chips}
      </div>
    </div>
  </section>
'''

def visual_block(p):
    if p.get('screenshot'):
        return f'''<div class="device-frame">
            <img src="../{esc(p['screenshot'])}" alt="Aperçu de l'application {esc(p['name'])}" loading="lazy">
          </div>'''
    return '''<div class="device-frame device-placeholder">
            <div class="placeholder-inner">
              <i class="bi bi-image" aria-hidden="true"></i>
              <span>Aperçu à venir</span>
            </div>
          </div>'''

def components_block(p):
    if not p.get('isFamily') or not p.get('components'): return ''
    cards = []
    for c in p['components']:
        role = '' if str(c.get('role', '')).startswith('TODO') else f"<p class=\"small mb-0\">{esc(c['role'])}</p>"
        cards.append(f'''        <div class="col-md-4">
          <div class="project-feature h-100">
            <span class="pf-icon"><i class="bi bi-box" aria-hidden="true"></i></span>
            <h3 class="h6">{esc(c['name'])}</h3>
            {role}
            <a href="{esc(c['url'])}" target="_blank" rel="noopener noreferrer" class="small">{esc(c['url'].replace('https://',''))} <i class="bi bi-box-arrow-up-right"></i></a>
          </div>
        </div>''')
    return f'''
  <section class="project-section" aria-labelledby="components-heading">
    <div class="container">
      <div class="text-center mb-5">
        <h2 id="components-heading" class="fw-bold">L'écosystème {esc(p['name'])}</h2>
        <p class="section-subtitle mx-auto">Les briques qui composent le produit.</p>
      </div>
      <div class="row g-4 justify-content-center">
{chr(10).join(cards)}
      </div>
    </div>
  </section>
'''

def responsible_notice(p):
    if not p.get('responsibleGamblingNotice'): return ''
    return '''
      <p class="text-muted small mt-4 mb-0">
        Les jeux d'argent et de hasard comportent des risques : endettement, isolement, dépendance.
        Interdits aux mineurs. Pour être aidé, appelez le 09 74 75 13 13 (appel non surtaxé).
      </p>'''

def cta_label(p):
    return p.get('cta') or f"Visiter {p['name']}"

PAGE_TPL = '''<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{name} — {category} | 0xLabs</title>
  <meta name="description" content="{name}, projet 0xLabs : {tagline}">
  <meta name="author" content="0xLabs">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://zeroxlabs.com/projets/{slug}.html">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://zeroxlabs.com/projets/{slug}.html">
  <meta property="og:title" content="{name} — {category} | 0xLabs">
  <meta property="og:description" content="{tagline}">
  <meta property="og:image" content="{og_image}">
  <meta property="og:site_name" content="0xLabs">
  <meta property="twitter:card" content="summary_large_image">
  <meta property="twitter:title" content="{name} — {category} | 0xLabs">
  <meta property="twitter:description" content="{tagline}">
  <meta property="twitter:image" content="{og_image}">

  <link rel="icon" type="image/png" href="../img/zeroxlabs-icon512x512.png">
  <link rel="apple-touch-icon" href="../img/zeroxlabs-icon512x512.png">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.10.5/font/bootstrap-icons.min.css" rel="stylesheet">
  <link href="../styles.css" rel="stylesheet">
</head>
<body class="project-page" style="--project-accent:{accent}; --project-accent-soft:{accent_soft};">
  <nav class="navbar navbar-expand-lg navbar-dark sticky-top" style="background-color: var(--primary-color);">
    <div class="container">
      <a class="navbar-brand d-flex align-items-center" href="/">
        <img src="../img/zeroxlabs-icon512x512.png" alt="Logo 0xLabs" class="logo me-3">
        <span class="d-none d-md-inline retro-title">0xLabs</span>
      </a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Ouvrir la navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto align-items-lg-center">
          <li class="nav-item"><a class="nav-link" href="/projets/">Projets</a></li>
          <li class="nav-item"><a class="nav-link" href="../zeroxware.html">Laboratoire</a></li>
          <li class="nav-item"><a class="nav-link" href="../team-fr.html">Équipe</a></li>
          <li class="nav-item ms-lg-2"><a class="nav-link btn btn-project px-3" href="{url}" target="_blank" rel="noopener noreferrer">Visiter l'app</a></li>
        </ul>
      </div>
    </div>
  </nav>

  <div class="container pt-3">
    <nav aria-label="Fil d'Ariane">
      <ol class="breadcrumb small mb-0">
        <li class="breadcrumb-item"><a href="/" class="text-decoration-none">Accueil</a></li>
        <li class="breadcrumb-item"><a href="/projets/" class="text-decoration-none">Projets</a></li>
        <li class="breadcrumb-item active" aria-current="page">{name}</li>
      </ol>
    </nav>
  </div>

  <header class="project-hero">
    <div class="container position-relative" style="z-index:2;">
      <p class="project-eyebrow"><i class="bi {icon} me-1" aria-hidden="true"></i> Produit 0xLabs · {category}</p>
      <h1>{name}</h1>
      <p class="project-tagline">{tagline}</p>
      <p class="mb-4">
        <span class="status-badge"><span class="status-dot"></span> {status}</span>
      </p>
      <div class="d-flex flex-wrap justify-content-center gap-3">
        <a href="{url}" target="_blank" rel="noopener noreferrer" class="btn btn-project btn-lg">
          <i class="bi bi-box-arrow-up-right me-2" aria-hidden="true"></i>{cta}
        </a>
        <a href="#apercu" class="btn btn-project-outline btn-lg">Voir l'aperçu</a>
      </div>
    </div>
  </header>

  <section class="project-section">
    <div class="container text-center">
      <p class="project-lead">{description}</p>
    </div>
  </section>

  <section class="project-section alt" aria-labelledby="features-heading">
    <div class="container">
      <div class="text-center mb-5">
        <h2 id="features-heading" class="fw-bold">Fonctionnalités clés</h2>
      </div>
      <div class="row g-4">
{features}
      </div>
    </div>
  </section>

  <section id="apercu" class="project-section" aria-labelledby="apercu-heading">
    <div class="container">
      <div class="row align-items-center g-5">
        <div class="col-lg-7">
          {visual}
        </div>
        <div class="col-lg-5">
          <h2 id="apercu-heading" class="fw-bold mb-3">Aperçu</h2>
          <p class="project-lead text-start mx-0">Découvrez {name} en conditions réelles, directement en ligne.</p>
          <a href="{url}" target="_blank" rel="noopener noreferrer" class="btn btn-project mt-3">
            <i class="bi bi-box-arrow-up-right me-2" aria-hidden="true"></i>{cta}
          </a>
        </div>
      </div>
    </div>
  </section>
{components}{tech}
  <section class="project-cta">
    <div class="container">
      <h2 class="fw-bold mb-3">Envie d'essayer {name} ?</h2>
      <p class="project-lead mb-4">{tagline}</p>
      <div class="d-flex flex-wrap justify-content-center gap-3">
        <a href="{url}" target="_blank" rel="noopener noreferrer" class="btn btn-project btn-lg">
          <i class="bi bi-box-arrow-up-right me-2" aria-hidden="true"></i>{cta}
        </a>
        <a href="/projets/" class="btn btn-outline-light btn-lg">← Tous les projets</a>
      </div>{responsible}
    </div>
  </section>

  <footer class="py-4 text-center">
    <div class="container">
      <p class="mb-2">&copy; 2025 0xLabs. Tous droits réservés.</p>
      <nav aria-label="Navigation du pied de page">
        <div class="d-flex justify-content-center flex-wrap gap-3 mt-3">
          <a href="/" class="text-decoration-none text-muted">Accueil</a>
          <span class="text-muted">|</span>
          <a href="/projets/" class="text-decoration-none text-muted">Projets</a>
          <span class="text-muted">|</span>
          <a href="../mentions-legales.html" class="text-decoration-none text-muted">Mentions légales</a>
          <span class="text-muted">|</span>
          <a href="../confidentialite.html" class="text-decoration-none text-muted">Confidentialité</a>
        </div>
      </nav>
    </div>
  </footer>

  <script type="application/ld+json">
  {jsonld}
  </script>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

def render_page(p):
    accent = p['accent']
    og_image = f"https://zeroxlabs.com/{p['screenshot']}" if p.get('screenshot') else "https://zeroxlabs.com/img/zeroxlabs-logo.png"
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": p['name'],
        "operatingSystem": "iOS" if "mobile" in p['category'].lower() else "Web",
        "applicationCategory": "GameApplication" if "Jeu" in p['category'] else "WebApplication",
        "url": p['url'],
        "description": p['description'],
        "creator": {"@type": "Organization", "name": "0xLabs", "url": "https://zeroxlabs.com"}
    }, ensure_ascii=False, indent=2)
    return PAGE_TPL.format(
        name=esc(p['name']), slug=p['slug'], category=esc(p['category']),
        tagline=esc(p['tagline']), description=esc(p['description']),
        accent=accent, accent_soft=hex_to_rgba(accent, 0.16),
        icon=project_icon(p), status=esc(p['status']), url=esc(p['url']),
        cta=esc(cta_label(p)), og_image=esc(og_image),
        features=feature_items(p['features']),
        visual=visual_block(p), tech=tech_chips(p.get('tech')),
        components=components_block(p), responsible=responsible_notice(p),
        jsonld=jsonld,
    )

# ---- Index page ----
def index_card(p):
    accent = p['accent']
    thumb = (f'<img src="../{esc(p["screenshot"])}" class="card-img-top project-thumb" alt="Aperçu de {esc(p["name"])}" loading="lazy">'
             if p.get('screenshot') else
             f'<div class="project-thumb d-flex align-items-center justify-content-center" style="color:{accent};"><i class="bi bi-image" style="font-size:2.5rem;"></i></div>')
    return f'''        <div class="col-md-6 col-lg-4">
          <div class="card project-card h-100 bg-dark text-light" style="border-color:{hex_to_rgba(accent,0.5)};">
            {thumb}
            <div class="card-body">
              <div class="d-flex align-items-center justify-content-between mb-2">
                <h2 class="h5 mb-0">{esc(p['name'])}</h2>
                <span class="badge" style="background:{hex_to_rgba(accent,0.16)};color:{accent};border:1px solid {accent};">{esc(p['status'])}</span>
              </div>
              <p class="small text-muted mb-2">{esc(p['category'])}</p>
              <p class="small mb-0">{esc(p['tagline'])}</p>
              <a href="{p['slug']}.html" class="stretched-link" aria-label="Découvrir {esc(p['name'])}"></a>
            </div>
          </div>
        </div>'''

def render_index(projects):
    cards = '\n'.join(index_card(p) for p in projects)
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Nos projets | 0xLabs</title>
  <meta name="description" content="Tous les produits 0xLabs en ligne : LotoBooster, ChillCards, Yearloop, The Age of Bryan et plus encore.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://zeroxlabs.com/projets/">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://zeroxlabs.com/projets/">
  <meta property="og:title" content="Nos projets | 0xLabs">
  <meta property="og:description" content="Tous les produits 0xLabs en ligne.">
  <meta property="og:image" content="https://zeroxlabs.com/img/zeroxlabs-logo.png">
  <link rel="icon" type="image/png" href="../img/zeroxlabs-icon512x512.png">
  <link rel="apple-touch-icon" href="../img/zeroxlabs-icon512x512.png">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.10.5/font/bootstrap-icons.min.css" rel="stylesheet">
  <link href="../styles.css" rel="stylesheet">
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-dark sticky-top" style="background-color: var(--primary-color);">
    <div class="container">
      <a class="navbar-brand d-flex align-items-center" href="/">
        <img src="../img/zeroxlabs-icon512x512.png" alt="Logo 0xLabs" class="logo me-3">
        <span class="d-none d-md-inline retro-title">0xLabs</span>
      </a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Ouvrir la navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto align-items-lg-center">
          <li class="nav-item"><a class="nav-link active" href="/projets/">Projets</a></li>
          <li class="nav-item"><a class="nav-link" href="../zeroxware.html">Laboratoire</a></li>
          <li class="nav-item"><a class="nav-link" href="../team-fr.html">Équipe</a></li>
        </ul>
      </div>
    </div>
  </nav>

  <header class="project-hero" style="padding:80px 0 60px;">
    <div class="container position-relative" style="z-index:2;">
      <p class="project-eyebrow">0xLabs · Portfolio</p>
      <h1>Nos projets</h1>
      <p class="project-tagline">Les produits que nous concevons, développons et faisons vivre — tous en ligne.</p>
    </div>
  </header>

  <section class="project-section">
    <div class="container">
      <div class="row g-4">
{cards}
      </div>
    </div>
  </section>

  <footer class="py-4 text-center">
    <div class="container">
      <p class="mb-2">&copy; 2025 0xLabs. Tous droits réservés.</p>
      <nav aria-label="Navigation du pied de page">
        <div class="d-flex justify-content-center flex-wrap gap-3 mt-3">
          <a href="/" class="text-decoration-none text-muted">Accueil</a>
          <span class="text-muted">|</span>
          <a href="../zeroxware.html" class="text-decoration-none text-muted">Laboratoire ZeroxWare</a>
          <span class="text-muted">|</span>
          <a href="../mentions-legales.html" class="text-decoration-none text-muted">Mentions légales</a>
          <span class="text-muted">|</span>
          <a href="../confidentialite.html" class="text-decoration-none text-muted">Confidentialité</a>
        </div>
      </nav>
    </div>
  </footer>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

ready = [p for p in data['projects'] if is_ready(p)]
for p in ready:
    out = os.path.join(ROOT, 'projets', f"{p['slug']}.html")
    open(out, 'w', encoding='utf-8').write(render_page(p))
    print('page  ->', out)

idx = os.path.join(ROOT, 'projets', 'index.html')
open(idx, 'w', encoding='utf-8').write(render_index(ready))
print('index ->', idx)
print('Projets générés:', [p['slug'] for p in ready])
