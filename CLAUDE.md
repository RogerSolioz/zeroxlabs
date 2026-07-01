# CLAUDE.md — 0xLabs (zeroxlabs.com)

Guide de travail pour ce dépôt. Lu automatiquement par Claude Code en local (VSCode/CLI) et en cloud (web/mobile).

## Ce qu'est ce projet

Site **vitrine** de 0xLabs : présente les produits du studio (déployés sur Netlify) et renvoie vers chaque app en ligne.

- **Site statique pur** : HTML + CSS + Bootstrap 5 via CDN. **Aucune étape de build**, pas de bundler, pas de framework JS.
- **Hébergement** : Netlify (`publish = "."` → la racine du repo est déployée telle quelle).
- **Langue** : **français** (tout le contenu visible est en FR ; `lang="fr"`).
- Pas de suite de tests ni de linter.

## Structure

```
index.html              Accueil (hero, expertise, réalisations, contact)
zeroxware.html          Laboratoire ZeroxWare (projets détaillés)
team-fr.html            Équipe   (team.html = redirection vers team-fr.html)
mentions-legales.html   Légal — contient des champs [À COMPLÉTER]
confidentialite.html    RGPD  — contient des champs [À COMPLÉTER]
thank-you.html          Confirmation d'envoi du formulaire
styles.css              TOUS les styles custom (thème sombre, variables CSS)
projets/
  projects.json         SOURCE UNIQUE des projets (données)
  index.html            Portfolio /projets/ (généré)
  <slug>.html           Page vitrine par projet (générée)
scripts/
  generate-projects.py  Génère les pages projet depuis projects.json
img/                    Logos, fonds, favicon, photos d'équipe (WebP)
import/                 Captures d'écran des projets (WebP)
netlify.toml, _redirects, sitemap.xml, robots.txt
```

## Système des pages projet (important)

`projets/projects.json` est la **source de vérité**. Les pages `projets/*.html` et `projets/index.html` sont **générées**, ne pas les éditer à la main.

**Ajouter / modifier un projet :**
1. Éditer `projets/projects.json` (voir le champ `_instructions` en tête du fichier).
2. Déposer une capture dans `import/` (voir « Images » ci-dessous) et référencer son chemin dans `screenshot`.
3. Régénérer :
   ```bash
   python3 scripts/generate-projects.py
   ```
4. Ajouter la nouvelle page à `sitemap.xml` et câbler une carte sur l'accueil (`index.html`, section `#realisations`) si pertinent.

Un projet dont `category` commence par `TODO` est ignoré par le générateur (contenu incomplet).
Accent couleur par projet via la variable CSS `--project-accent` (posée en inline sur `<body class="project-page">`).

## Conventions

- **Thème** : sombre, piloté par les variables CSS dans `:root` (`styles.css`). Réutiliser ces variables plutôt que des valeurs en dur.
- Le style « terminal néon vert » (`.retro-title`) est réservé à **la marque/logo**, jamais au corps de texte (police Inter).
- **Accessibilité** : `alt` sur les images, `aria-label` sur les liens/boutons icônes, `loading="lazy"` sur les images sous la ligne de flottaison.
- Liens externes : `target="_blank" rel="noopener noreferrer"`.
- Ne pas réintroduire l'ancien positionnement fictif (ZeroxVerse/ZeroxTime) ni le meme-coin DOWGE (supprimés volontairement).

## Images (à respecter — le repo a été optimisé de ~31 Mo à ~0,8 Mo)

- **Toujours livrer en WebP** (JPEG progressif seulement pour les og:image sociales, PNG seulement pour favicon/logo à transparence).
- **Ne jamais committer de PNG/JPEG lourds** (> ~200 Ko) : redimensionner à la taille d'affichage réelle avant conversion.
- Outil dispo sans dépendance système : **Pillow** (`pip install pillow`).
  ```python
  from PIL import Image
  im = Image.open("source.png")
  if im.width > 1100:  # cap selon l'usage (captures ~1100, photos ~300)
      im = im.resize((1100, round(im.height*1100/im.width)), Image.LANCZOS)
  im.save("import/mon-projet.webp", "WEBP", quality=80, method=6)
  ```

## Prévisualiser en local

Site statique — un simple serveur suffit :
```bash
python3 -m http.server 8000   # puis http://localhost:8000
```
Bootstrap et Bootstrap Icons sont chargés par **CDN** : en environnement réseau restreint (certaines sessions cloud), la grille et les icônes ne s'affichent pas — c'est normal, elles fonctionnent en production sur Netlify.

## Git & déploiement

- Netlify déploie sur push. Formulaire de contact via **Netlify Forms** (`data-netlify="true"`).
- Travailler sur une branche, committer par lots cohérents, pousser. Ne pas pousser sur `main` sans raison.
- Après avoir touché aux images ou aux pages projet, vérifier les liens : aucun `href`/`src` interne ne doit pointer vers un fichier absent.

## Services externes liés (hors de ce repo)

- **Netlify** : hébergement de la vitrine ET des produits (voir le compte pour la liste).
- **Supabase** : backends de certains produits (ex. ChillCards, Bookatomy). La vitrine elle-même n'utilise pas de base de données.
- Projets exclus de la vitrine pour l'instant : `katiart`.

## Points ouverts (à compléter)

- `projets/projects.json` : contenu `TODO` pour **Quiadit** et **Bookatomy** (+ rôle des sous-sites app/lexatomy/pubdom).
- Pages légales : renseigner les champs `[À COMPLÉTER]` (identité de l'éditeur, SIRET, directeur de publication, e-mail).
