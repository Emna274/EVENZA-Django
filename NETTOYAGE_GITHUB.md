# Nettoyage et publication d’Évenza

## Fichiers retirés

| Éléments | Motif |
| --- | --- |
| `.dependency-download/split-evenza.py`, `split-forms.py`, `split-views.py`, `finish-layout.py`, `state-migrations.py`, `apply-architecture.py` | Scripts utilisés une seule fois pour la refactorisation et sa vérification |
| `.dependency-download/refonte-qa.cjs`, `refonte-fix-fixtures.py` | Script Chrome et préparation des données de contrôle. Les tests Django restent dans le dépôt. |
| `.dependency-download/refonte-dashboard.png`, `refonte-events.png`, `refonte-login.png`, `refonte-mobile.png` | Captures produites pendant le contrôle |
| `.dependency-download/refonte-qa.sqlite3`, `architecture-rehearsal-v1.sqlite3`, `architecture-rehearsal-f79cab3a.sqlite3` | Base de fixtures et copies jetables de répétition. La base de travail et sa sauvegarde de référence restent en place. |
| `gestion/migrations/__init__.py`, `gestion/templatetags/__init__.py` | Marqueurs vides des anciens répertoires, après déplacement des migrations et de la bibliothèque de tags |
| 125 fichiers `.pyc` dans `apps/`, `config/` et `gestion/` | Caches automatiquement régénérés par Python |

## Fichiers conservés et éléments à valider

Tous les modèles, vues, formulaires, tests Django, routes, migrations, templates, feuilles de style, scripts et visuels nécessaires à l’application sont conservés. Les assets de tailles différentes servent à l’affichage selon l’écran ou l’emplacement. La base `db.sqlite3`, la sauvegarde locale sous `backups/` et les fichiers privés restent en place et sont exclus de Git.

| Élément conservé localement | Point à valider |
| --- | --- |
| `app/`, `database/` et `storage/` | Utilité du prototype PHP et de son schéma pour les travaux du groupe |
| `.dependency-download/preview.sqlite3` | Contenu de l’aperçu historique, traité comme une base à préserver |
| `.dependency-download/refactor-legacy-*.py` et `rehearse-architecture.py` | Utilité de l’archive de code et de la répétition de migration |
| `.venv/`, `.vendor/` et les roues locales | Environnement courant et dépendances de travail |
| `evenementiel/`, `evenza-application/`, `evenza-atelier/`, `evenza-ivoire/`, présentations, scripts de maquette et archives dans le dossier parent | Références et livrables historiques en dehors du dépôt Django |

## Architecture et configuration

Le dépôt Git est initialisé dans `evenza/`. `apps/` contient les six gestions, `accounts`, `dashboard` et les utilitaires transmis par `core`. `config/`, `templates/` et `static/` regroupent la configuration et les composants communs. `media/.gitkeep` matérialise le dossier de médias, dont les fichiers restent locaux. `gestion/models.py` conserve deux imports utilisés par la migration historique.

Django lit `.env` à l’aide de `python-dotenv`, la priorité revenant à l’environnement du processus. La clé de signature est obligatoire et une clé aléatoire a été générée dans la configuration locale. Les anciennes sessions signées avec la clé de développement peuvent nécessiter une nouvelle connexion. Le modèle `.env.example` est publiable et documente SQLite, les hôtes et les options SMTP. Les mots de passe utilisés dans les tests sont générés pendant leur exécution.

Le périmètre versionné exclut les fichiers `.env` privés, les bases, les sauvegardes, les médias, les archives locales et les réglages d’IDE. Les métadonnées du commit initial utilisent une identité de projet et une adresse non personnelle.

## Contrôles

- `pip check` a confirmé la cohérence des dépendances.
- `python manage.py check`, `python manage.py makemigrations --check --dry-run` et `python manage.py migrate --check` ont réussi.
- Les 27 tests Django ont réussi. Ils couvrent les six CRUD, les rôles, la connexion, les documents privés et le tableau de bord.
- Une copie extraite de l’index Git a démarré avec un nouveau `.env` et une base neuve. Les migrations, le contrôle Django et les 27 tests y ont également réussi.
- Chrome a chargé l’authentification, le tableau de bord, les listes et formulaires des six gestions, et les ressources statiques. Les parcours ont été contrôlés à 320, 390, 768 et 1 440 pixels sur une base de test isolée.
- Les 183 fichiers de l’index initial ont été contrôlés pour exclure les fichiers privés et rechercher les clés, identifiants, adresses personnelles et valeurs sensibles. Les 10 migrations ont été retrouvées dans l’index.

## GitHub et collaboration

Le commit initial est préparé sur `main`, avec une branche locale `develop`. Aucun dépôt distant n’est configuré. Le dépôt demandé est **EVENZA-Django**, en visibilité privée, avec la description « ÉVENZA — Plateforme collaborative de gestion événementielle développée avec Django. ». La création et le premier envoi attendent la confirmation. Le lien exact sera renseigné après vérification sur GitHub.

GitHub CLI ne figure pas sur le PATH et aucune connexion GitHub exploitable n’a été confirmée. Une fois GitHub CLI installé, ouvrez un nouveau PowerShell et terminez l’authentification dans votre navigateur. [Installation officielle GitHub CLI](https://github.com/cli/cli#installation) · [Manuel de connexion GitHub CLI](https://cli.github.com/manual/gh_auth_login)

```powershell
gh auth login --hostname github.com --git-protocol https --web
gh auth status --hostname github.com
```

Une fois le dépôt disponible, le propriétaire invite les collègues via **Settings → Collaborators → Add people**. Les membres acceptent l’invitation, copient l’URL HTTPS depuis **Code**, puis clonent le dépôt. Le [README](README.md) explique l’installation Windows et l’usage de `main`, `develop` et des branches `feature/<gestion>` avec des Pull Requests. [Documentation GitHub sur les collaborateurs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/inviting-collaborators-to-a-personal-repository)
