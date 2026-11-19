# Évenza

Évenza est une plateforme collaborative de gestion événementielle. Elle centralise les dossiers d’événements, les participants, les prestataires, les programmes et les ressources. Le tableau de bord affiche les indicateurs et le calendrier selon le rôle de la personne connectée.

## Technologies

Python 3.13, Django 5.2, SQLite, templates Django, Bootstrap 5 et Chart.js. Les ressources d’interface sont fournies dans le projet.

## Architecture et gestions

| Application | Responsabilité |
| --- | --- |
| `apps/evenements/` | Demandes, planification, validation et suivi des événements |
| `apps/prestataires/` | Prestataires, catalogue de services et réservations |
| `apps/utilisateurs/` | Comptes, rôles et activation |
| `apps/programmes/` | Sessions et suggestions de programme |
| `apps/participants/` | Inscriptions, invitations, présences, réclamations et documents |
| `apps/ressources/` | Inventaire, disponibilités et affectations |

`apps/accounts/` gère l’authentification, le profil et les notifications. `apps/dashboard/` présente les statistiques, le calendrier et l’activité. `apps/core/` contient les composants partagés. `config/` contient les paramètres et les routes principales. Les templates communs sont dans `templates/`, les ressources d’interface dans `static/` et les fichiers locaux téléversés sont exclus de Git.

## Installation sous Windows

Installez Git et Python 3.13. Après avoir accepté l’invitation au dépôt privé, copiez son URL HTTPS via **Code** sur GitHub. Remplacez `PROPRIETAIRE` par le compte ou l’organisation affiché dans cette URL.

```powershell
git clone https://github.com/PROPRIETAIRE/EVENZA-Django.git
cd EVENZA-Django
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si l’activation est indisponible, utilisez `.\.venv\Scripts\python.exe` à la place de `python` pour les commandes suivantes.

### Configuration locale

Créez `.env` à partir de `.env.example` et générez une clé locale avec cette commande. Le mode `x` protège un éventuel fichier existant.

```powershell
python -c "import secrets; from pathlib import Path; template=Path('.env.example').read_text(encoding='utf-8'); f=Path('.env').open('x', encoding='utf-8'); f.write(template.replace('DJANGO_SECRET_KEY=', 'DJANGO_SECRET_KEY='+secrets.token_urlsafe(64), 1)); f.close()"
```

L’exemple active le mode développement et utilise `db.sqlite3`. `DJANGO_ALLOWED_HOSTS` accepte une liste d’hôtes séparés par des virgules. Les courriels s’affichent dans le terminal Django tant que le backend SMTP facultatif reste désactivé.

### Base et serveur

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Ouvrez [Évenza en local](http://127.0.0.1:8000/) et connectez-vous avec le superutilisateur créé. Pour une base existante, la commande `migrate` suffit avant de relancer Django et de réutiliser vos comptes.

### Vérifications

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

## Collaboration sur GitHub

- `main` contient la version stable. `develop` rassemble les changements avant la validation de la version suivante.
- Chaque gestion utilise une branche courte, par exemple `feature/participants`, créée depuis `develop`.
- Ouvrez une Pull Request de la branche de travail vers `develop`. Le groupe peut relire les changements et exécuter les tests avant la fusion. Les versions validées sont intégrées par Pull Request de `develop` vers `main`.
- Ajoutez aux commits les migrations liées à vos modifications de modèles. Conservez vos configurations, bases, médias et accès privés sur votre poste.

```powershell
git switch develop
git pull --ff-only
git switch -c feature/participants
```

Après publication, le propriétaire peut ouvrir **Settings → Collaborators → Add people** dans GitHub et inviter chaque membre. Chacun accepte l’invitation puis utilise **Code** pour copier l’URL du dépôt. [Documentation GitHub sur les collaborateurs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/inviting-collaborators-to-a-personal-repository)

## Documentation

[Architecture et migrations](ARCHITECTURE_DJANGO.md) · [Rapport de développement](RAPPORT_DEVELOPPEMENT.md) · [Refonte visuelle](RAPPORT_REFONTE_VISUELLE.md) · [Nettoyage et publication](NETTOYAGE_GITHUB.md)
