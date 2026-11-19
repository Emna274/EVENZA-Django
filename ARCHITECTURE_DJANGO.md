# Architecture Django d’Évenza

## 1. Avant la refactorisation

L’application `gestion` regroupait les 16 modèles, les formulaires, les vues, les routes, les déclarations d’administration et les tests des six gestions. Elle gérait également l’authentification, les notifications et le tableau de bord. La configuration se trouvait déjà dans `config/`. Les templates étaient regroupés à la racine et les styles, scripts et images étaient servis par `static/`.

L’audit initial a trouvé deux migrations appliquées pour `gestion`, 20 entrées dans le journal des migrations, une base SQLite intègre sans relation orpheline et 26 tests Django réussis.

## 2. Architecture actuelle

```text
evenza/
  config/                       Configuration, URL racines, ASGI, WSGI
  apps/
    evenements/                 Événements
    prestataires/               Prestataires, services et réservations
    utilisateurs/               Comptes utilisateurs et rôles
    programmes/                 Sessions et suggestions
    participants/               Inscriptions, réclamations et documents
    ressources/                 Inventaire et affectations
    accounts/                   Connexion, profil, notifications et alertes
    dashboard/                  Tableau de bord, calendrier et activité
    core/                       Composants Python partagés
  gestion/                      Compatibilité des imports sérialisés en 0001
  templates/                    Layout, composants et écrans CRUD communs
  static/                       Styles, scripts, polices et images
  backups/                      Sauvegarde SQLite locale, ignorée par Git
```

Chaque application métier possède son `AppConfig`, ses modèles, vues, formulaires, routes, administration, tests, migrations et templates dédiés. Lorsqu’un écran a le même fonctionnement dans plusieurs gestions, ses éléments communs restent dans `templates/gestion/` ou `templates/components/`. Les fichiers statiques existants restent communs.

## 3 et 4. Applications métier et responsabilités

| Application | Modèles | Responsabilité |
| --- | --- | --- |
| `apps.evenements` | `Event` | Demandes, planification, validation et suivi des événements |
| `apps.prestataires` | `Provider`, `Service`, `Reservation` | Catalogue, services, tarifs et réservations |
| `apps.utilisateurs` | `User` | Gestion des utilisateurs, des rôles et de l’activation des comptes |
| `apps.programmes` | `Program`, `Suggestion` | Sessions, programmation et validation des suggestions |
| `apps.participants` | `Participant`, `Complaint`, `Document` | Inscriptions, invitations, présence, badges, réclamations et documents |
| `apps.ressources` | `Resource`, `Allocation` | Inventaire, contrôle de disponibilité et affectation aux événements |

`apps.accounts` gère les parcours d’authentification, le profil, les notifications et les alertes de connexion. `apps.dashboard` gère les statistiques, les raccourcis, le calendrier et le journal `Activity`. Les deux applications référencent le même utilisateur que les six gestions.

`Event` reste le point de rattachement des programmes, inscriptions, réservations et affectations. Les réservations référencent un service, qui référence un prestataire. Les documents et réclamations référencent une inscription. Les comptes référencés et les relations Django vers les groupes et permissions conservent leurs clés.

## 5 et 6. Déplacements et imports

- Les classes de `gestion/models.py` ont été déplacées vers les `models.py` de leurs applications. Le modèle abstrait `Period` se trouve dans `apps/core/models.py`. `gestion/models.py` réexporte uniquement `UserManager` et `badge_token`, dont les chemins sont sérialisés dans la migration historique.
- Les anciens `gestion/views.py` et `gestion/forms.py` ont été répartis entre les applications. Les classes génériques restent dans `apps/core/views.py` et `apps/core/forms.py`. Les actions spécifiques restent dans leur domaine. Les sections sont déclarées localement, puis regroupées dans `apps/core/access.py` pour la navigation et le filtrage par rôle.
- Les déclarations d’administration et les tests sont répartis par application. Les fixtures et assertions CRUD réutilisées sont dans `apps/core/test_support.py`.
- Les templates de connexion, de récupération, de profil et de notifications sont dans `apps/accounts/templates/`. Le tableau de bord et sa bibliothèque `evenza_ui` sont dans `apps/dashboard/`. Les écrans propres aux gestions sont sous `apps/<gestion>/templates/<gestion>/`.
- `config/settings.py` charge les huit applications et les nouveaux chemins de la bibliothèque de tags et du processeur de navigation. Les clés étrangères vers le compte utilisent `settings.AUTH_USER_MODEL`. Les dépendances inverses nécessaires aux validations utilisent les relations existantes ou des imports locaux.

## 7. URL

`config/urls.py` connecte chaque application avec `include()`. Les URL publiques et les noms de routes conservent leurs chemins, y compris les six namespaces métier, les routes de compte, les invitations, les actions, les badges et les documents. Pour les modèles déplacés, les anciens liens et noms de routes d’administration `admin:gestion_…` restent accessibles par alias. L’index de l’administration regroupe les modèles sous leurs applications actuelles.

## 8. Conservation des données

La sauvegarde locale `backups/evenza-avant-refactorisation-20261119-232809.sqlite3` a été créée par l’API de sauvegarde SQLite avant les changements et est exclue du dépôt. Les deux migrations d’origine ont été déplacées vers `apps/utilisateurs/migrations/`. Le label interne de cette application reste `gestion`, ce qui conserve `AUTH_USER_MODEL = "gestion.User"`, la table `gestion_user` et l’historique de migration authentification.

Les nouvelles applications gardent les noms de tables, contraintes et index en place. `gestion.0003` retire les modèles transférés de l’ancien état de migration. Les migrations initiales des autres applications les enregistrent sous leurs labels respectifs avec `SeparateDatabaseAndState`. La transition exécute des changements d’état Django et une mise à jour des labels des types de contenu. Les identifiants des types de contenu, des permissions, des journaux d’administration et des attributions directes ou par groupe restent identiques. Aucune table métier n’est créée, renommée ou supprimée pendant la transition de la base existante. [Documentation Django sur SeparateDatabaseAndState](https://docs.djangoproject.com/en/5.2/ref/migration-operations/#separatedatabaseandstate)

Après application à `db.sqlite3`, le schéma SQLite, les identifiants des types de contenu et le contenu des 22 tables comparées sont identiques. `PRAGMA integrity_check` et `PRAGMA foreign_key_check` ont réussi. Le chemin des médias et le dossier `storage/` ont été conservés. L’audit n’a trouvé aucun fichier média déposé sur la base de travail. Un document binaire a été vérifié sur la copie de répétition.

Pour mettre à jour une autre copie existante, sauvegardez-la puis exécutez `python manage.py migrate`. La migration annule la transition si un modèle possède déjà deux types de contenu concurrents, afin de préserver les références.

## 9. Vérifications

- Les 26 tests initiaux ont réussi avant la refactorisation. Les **27 tests** finaux réussissent sur une base neuve, dont une vérification supplémentaire des anciens liens d’administration et de l’identité de `User`.
- `python manage.py check`, `python manage.py makemigrations --check --dry-run` et `python manage.py migrate --check` ont réussi.
- La répétition sur une copie de la sauvegarde enrichie a validé la migration, son annulation, puis sa réapplication. Elle a comparé le schéma, les données, les séquences et les identifiants. Elle a aussi vérifié les permissions attribuées à un compte et à un groupe, un journal d’administration, les relations et le document binaire.
- Le serveur Django a démarré sur une base isolée. Le contrôle Chrome automatisé a vérifié l’authentification, le tableau de bord, les listes et formulaires des six gestions, la navigation, le calendrier, les graphiques, le chargement des images et l’affichage de 320 à 1 440 px. Les parcours CRUD, les documents et les permissions sont également couverts par la suite Django.
- Les deux scripts JavaScript existants passent la vérification de syntaxe Node.js.

## 10. Problèmes rencontrés et solutions

Le déplacement des modèles changeait par défaut leur table et leurs types de contenu. Les tables et index ont été déclarés explicitement, et les opérations ont été limitées à l’état Django et au renommage des labels des types de contenu. Un import du mixin de formulaire des documents a été rétabli pendant l’assemblage des applications. Le premier script de répétition s’exécutait depuis un dossier auxiliaire et ne trouvait pas `config`. L’ajout du dossier du projet à son chemin Python a permis d’exécuter les trois phases sur une nouvelle copie.

Le design, les feuilles de style, les scripts, les images et les parcours existants ont été conservés. Les noms internes des permissions des modèles déplacés suivent leurs nouvelles applications, par exemple `evenements.view_event`. Les attributions enregistrées restent valides. Le modèle utilisateur conserve son label historique.
