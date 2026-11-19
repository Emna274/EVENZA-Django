# Rapport de développement Évenza

## 1. Architecture

Évenza est une application Django 5.2, avec Django Template Language, SQLite, Bootstrap 5, Bootstrap Icons et Chart.js. Le projet se lance depuis `evenza/`. La maquette `evenza-application/evenza-application.html` a servi de référence pour la palette ivoire et bordeaux et la typographie à empattements. Les versions HTML existantes, le code PHP, le schéma SQL et les présentations d’origine sont conservés.

- `config/` configure les URL racines, l’authentification, SQLite et les fichiers statiques.
- `gestion/` contient les modèles, les formulaires, les règles d’accès, les vues génériques, les URL et les tests. Une application métier commune facilite les relations et le partage de code. Chacune des six gestions dispose d’un espace de noms d’URL.
- `templates/` contient les écrans rendus par Django et leurs composants partagés.
- `static/` contient les styles, les scripts et les dépendances graphiques locales avec leurs licences.
- `gestion/migrations/` contient le schéma initial et la migration des libellés de choix.

## 2. Les six gestions

Les intitulés s’appuient sur la maquette et le backlog. Les rubriques secondaires reprennent les entités de `app/Modules.php` et du schéma PHP `database/schema.sql`.

| Gestion | URL locale | Rubriques |
| --- | --- | --- |
| Gestion des événements | `/evenements/` | Événements |
| Gestion des prestataires | `/prestataires/` | Prestataires, services, réservations |
| Gestion des utilisateurs | `/utilisateurs/` | Utilisateurs |
| Gestion des programmes | `/programmes/` | Sessions, suggestions |
| Gestion des participants | `/participants/` | Inscriptions, réclamations et documents associés |
| Gestion des ressources | `/ressources/` | Inventaire, affectations |

## 3. Modèles Django

`User` représente les cinq rôles du projet. `Event`, `Provider`, `Service`, `Reservation`, `Program`, `Suggestion`, `Participant`, `Complaint`, `Document`, `Resource` et `Allocation` reprennent les principales entités métier. `Activity`, `Notification` et `LoginAttempt` reprennent l’historique, les notifications et les tentatives de connexion du schéma. `LoginAlert` matérialise la détection des accès suspects demandée dans le backlog.

Le modèle d’authentification natif ajoute les champs techniques de connexion, d’accès à l’admin et de permissions. Les documents privés utilisent un champ binaire `Document.content` dans SQLite à la place de la référence à un fichier stocké par PHP. Les mots de passe et les liens de réinitialisation utilisent les mécanismes de Django.

## 4. Relations

| Entité | Relations |
| --- | --- |
| Événement | Un client, un organisateur et un validateur administrateur facultatifs |
| Prestataire | Un compte prestataire facultatif, plusieurs services |
| Réservation | Un événement et un service, avec le prestataire accessible via le service |
| Session ou suggestion | Un événement |
| Inscription | Un événement et un compte participant facultatif, plusieurs réclamations et documents |
| Affectation | Un événement et une ressource |
| Notification et activité | Un utilisateur destinataire ou auteur, selon le modèle |

La relation organisateur–événement suit la clé étrangère du schéma PHP avec un organisateur par événement. Le diagramme de classes présente aussi une association distincte `AffectationOrganisateur`. Les dépendances métier utilisent `PROTECT`. La suppression d’une fiche liée affiche une explication et permet de revenir aux enregistrements associés. Les activités restent consultables après suppression du compte auteur.

## 5. CRUD

Les six gestions disposent de pages d’ajout, liste, détail, modification et confirmation de suppression. Les opérations couvrent aussi les services, réservations, suggestions, réclamations et affectations. Les vues reposent sur `ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView` et des `ModelForm`. Les listes offrent recherche multicritère, filtres métier, pagination par 12 et export CSV des résultats. Les suppressions passent par POST et CSRF. Les droits peuvent limiter les opérations visibles et leur exécution.

## 6. Templates

`base.html` définit la navigation et l’en-tête. `dashboard.html` affiche l’accueil. Les templates de `gestion/` couvrent listes, onglets, pagination, détails, formulaires, confirmations, profil et notifications. `registration/` couvre connexion, inscription et mots de passe. L’interface utilise des grilles adaptatives, une navigation latérale repliable et des tableaux à défilement horizontal sur petits écrans.

## 7. Fonctionnalités avancées

- **Événements** — demandes client, suivi des statuts, confirmation par un administrateur, annulation et notification. Les dates et la capacité tiennent compte des inscriptions et des sous-fiches associées.
- **Prestataires** — catalogue avec recherche par spécialité ou ville, disponibilités déclarées, services et tarifs, acceptation ou refus, annulation et évaluation des réservations.
- **Utilisateurs** — inscription, profil, disponibilités et compétences, suivi de la charge d’un organisateur, gestion des rôles et de l’activation, limitation des tentatives de connexion et alertes consultables dans l’administration Django.
- **Programmes** — recherche par titre ou intervenant, filtre par date et événement, contrôle des bornes de l’événement, création de suggestions et validation vers une session ou rejet.
- **Participants** — contrôle de capacité et des conflits horaires, liste d’attente et attribution d’une place libérée, invitations signées et rappels par e-mail, catégories, préférences et placement manuel, présence manuelle ou par QR, documents privés, réclamations et avis après l’événement.
- **Ressources** — inventaire, consultation de la quantité disponible sur un créneau, historique des affectations, annulation et détection du pic de quantité réservée simultanément. La capacité et le stock sont vérifiés dans des transactions d’écriture SQLite.

## 8. Dashboard

Le tableau de bord interroge la base pour les compteurs des modules, les événements à venir, les activités récentes, les dates de début par mois et la répartition des événements par statut. Les graphiques Chart.js disposent de tableaux de données consultables. Les compteurs, raccourcis et listes tiennent compte du rôle connecté. La base de développement démarre vide.

## 9. Authentification et permissions

La connexion par e-mail, le hachage des mots de passe, les sessions, la réinitialisation et la déconnexion par POST reposent sur `django.contrib.auth`. Les formulaires POST utilisent CSRF. Les pages privées utilisent `LoginRequiredMixin` ou `login_required`. Les règles d’accès aux gestions sont décrites dans `gestion/modules.py`, puis appliquées aux listes, fiches, écritures et sélecteurs de relations. L’organisateur travaille sur ses événements, le prestataire sur ses prestations, le client sur ses demandes et le participant sur ses inscriptions. Le superutilisateur administre également les groupes et permissions de l’administration native sur `/admin/`.

## 10. Tests réalisés

- `python manage.py check` a réussi sans erreur.
- `python manage.py makemigrations --check --dry-run` a confirmé que les migrations correspondent aux modèles.
- `python manage.py migrate` a appliqué les migrations. `python manage.py migrate --check` a confirmé leur état.
- Les 23 tests de `python manage.py test` ont réussi sur une base isolée. Ils couvrent les six CRUD, les rubriques secondaires, la navigation, la recherche, la pagination, les exports, les permissions, la sécurité des documents, CSRF, les conflits horaires, la capacité, les courriels, le dashboard et le pointage QR.
- Syntaxe des deux scripts applicatifs avec `node --check`. Résolution des fichiers Bootstrap, Bootstrap Icons et Chart.js avec `manage.py findstatic`.
- Réponses HTTP 200 de la page de connexion, du tableau de bord et de ses fichiers statiques sur le serveur local. La vérification visuelle automatisée dans Chrome s’est interrompue, car l’outil de contrôle ne pouvait pas confirmer l’URL active.

## 11. Erreurs rencontrées et corrections

- Le premier lancement des tests a révélé une mauvaise importation du module de messagerie. L’import a été corrigé et la suite a été relancée.
- Django déduisait des libellés anglais à partir des noms internes de choix. La migration `0002` fixe explicitement les libellés français en conservant les valeurs stockées.
- Le premier téléchargement de `qrcode` était inaccessible à Python depuis le bac à sable après installation directe. La dépendance a été installée depuis une roue locale dans l’environnement virtuel et la génération SVG a été vérifiée par test.
- Les assertions de liste des réservations et affectations attendent le lien de la fiche. Le tableau affiche le service ou la ressource et l’événement dans des colonnes distinctes.

## 12. Lancement

La configuration actuelle et la génération du fichier `.env` sont décrites dans le [README](README.md). Configurez `.env` après l’installation des dépendances, avant les commandes Django ci-dessous.

Depuis le dossier `SE`, dans PowerShell :

```powershell
cd evenza
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Ouvrez [la page de connexion locale](http://127.0.0.1:8000/). Dans un environnement Python où les dépendances sont déjà installées, la commande directe est `python manage.py runserver`. Le serveur utilise `db.sqlite3` dans `evenza/`. `DJANGO_DB_PATH` permet de choisir une autre base SQLite.

Le serveur de développement écrit les courriels dans la console. Pour utiliser une messagerie réelle, configurez `DJANGO_EMAIL_BACKEND` avec `django.core.mail.backends.smtp.EmailBackend`, puis renseignez `DJANGO_EMAIL_HOST`, `DJANGO_EMAIL_PORT`, `DJANGO_EMAIL_USER`, `DJANGO_EMAIL_PASSWORD`, `DJANGO_EMAIL_TLS` selon le fournisseur et `DJANGO_FROM_EMAIL`. Pour scanner un badge depuis un autre appareil, l’adresse d’Évenza inscrite dans le QR doit être joignable depuis cet appareil.

## 13. Fonctionnalités du backlog encore ouvertes

- Le chatbot et la génération IA de suggestions exigent la définition d’une intégration et de ses données autorisées. Le cycle de suggestions saisies par l’équipe, validées ou rejetées, est disponible.
- L’affectation automatique des organisateurs demande des disponibilités horodatées et une règle de répartition. Le projet conserve les disponibilités en texte libre, la charge de travail et l’affectation manuelle.
- Le placement automatique par table exige un plan de salle et les règles de priorité des préférences. Les préférences et l’attribution manuelle avec contrôle d’unicité sont disponibles.
- La vérification intelligente des profils, l’analyse des besoins de formation et la personnalisation visuelle des badges restent à définir. Les contrôles de champs, les compétences, le badge QR standard et les alertes de connexion sont disponibles.
- Le transport SMTP réel requiert une configuration de messagerie. Les flux ont été testés avec le backend de messagerie de test Django. Le schéma MySQL et les données de démonstration du navigateur n’ont fait l’objet d’aucun transfert automatique.
