# Refonte visuelle Évenza

## Pages améliorées

| Surface | Refonte |
| --- | --- |
| Connexion, inscription et récupération | Panneau photographique, slogan et signature Évenza, champs avec icônes, erreurs à proximité des champs et accès direct aux parcours du compte. La composition passe en une colonne sur mobile. |
| Tableau de bord | Bannière de gala, indicateurs, cartes des prochains événements avec date, lieu et statut, calendrier mensuel, activité récente, graphiques Chart.js et accès rapides. |
| Événements | Bandeau illustré, miniatures par type, dates, lieux et statuts lisibles. |
| Prestataires | Catalogue avec bascule tableau/cartes, spécialité, ville, contact et statut. Les services et les réservations reprennent la même identité de module. |
| Utilisateurs | Avatars à initiales, état des comptes, rôle mis en évidence et formulaires harmonisés. |
| Programmes | Accent terracotta, icône de planning, filtres par événement et date pour les sessions et suggestions. |
| Participants | Avatars à initiales, statuts d’inscription, accès aux réclamations, aux badges et aux documents. |
| Ressources | Accent sauge, présentation de l’inventaire, badges d’état, historique des affectations et vérification de disponibilité. |
| Fiches, formulaires et confirmations | En-têtes par module, fil d’Ariane, actions visibles, présentation des champs et des relations. Les confirmations de suppression conservent leur parcours Django. La suppression de document utilise une boîte de dialogue accessible lorsqu’elle est prise en charge. |
| Paramètres, notifications, invitations, présence QR et pages d’erreur | Ces écrans reprennent la nouvelle navigation, les composants de formulaire, les surfaces et les messages Évenza. |
| Administration Django | Habillage colorimétrique et typographique de l’administration native. |

## Fichiers et composants

- `templates/base.html` centralise la navigation, l’en-tête, le fil d’Ariane, la coque d’authentification et la boîte de dialogue. `templates/dashboard.html` compose la vue d’ensemble.
- `templates/components/` contient la signature de marque, le calendrier, les pastilles d’état, les actions d’une fiche, les en-têtes de module et les états vides.
- Dans `templates/gestion/`, les templates `list.html`, `detail.html`, `form.html`, `fields.html`, `delete.html`, `messages.html`, `notifications.html` et `profile.html` ont été modifiés. Dans `templates/registration/`, `login.html`, `form.html` et `status.html` reprennent les nouveaux composants de compte. `templates/admin/base_site.html` charge l’habillage de l’interface native.
- `static/css/evenza.css` regroupe la palette, les thèmes des six modules, la typographie, les espacements, les bordures, les ombres et les styles responsives. `static/css/admin-evenza.css` cible l’administration Django.
- `static/js/evenza.js` gère le menu mobile, son focus clavier et la confirmation de document. `static/js/dashboard.js` adapte les graphiques à la palette et aux préférences de mouvement.
- `gestion/templatetags/evenza_ui.py` fournit les fonctions de présentation. Le calendrier réutilise la portée existante des événements et renvoie vers le filtre Django de la liste. La bascule des prestataires conserve la pagination, la recherche et l’export via les paramètres d’URL.
- `gestion/tests.py` ajoute trois régressions ciblées pour le calendrier, les actions de création selon le rôle et la vue prestataire par cartes.

## Identité et accessibilité

La palette associe bordeaux `#542D3B`, ivoire `#F7F2EA`, champagne `#C99B69`, rose poudré `#D9A6A3` et anthracite `#292128`. Playfair Display et DM Sans sont servies en WOFF2 depuis `static/fonts/`, avec leurs fichiers de licence OFL. Les actions comportent des libellés accessibles, les états sont exprimés en texte et en couleur, les champs et la navigation ont un focus visible et les graphiques disposent de tableaux de données. Le menu mobile prend le focus à l’ouverture, se ferme avec Échap et rend le focus à son bouton.

Les photographies sont des illustrations générées pour Évenza avec l’outil ImageGen intégré. Les cartes choisissent un visuel en fonction du type d’événement, avec le gala comme visuel par défaut. Ces images illustrent les catégories et ne représentent pas les lieux ou événements enregistrés. Toutes sont servies en WebP, avec une version mobile pour la photo de connexion et des variantes légères pour les cartes. Les visuels hors écran sont chargés à la demande.

| Visuel | Fichiers dans `static/images/` |
| --- | --- |
| Réception de mariage | `reception.webp`, `reception-mobile.webp`, `reception-card.webp` |
| Gala | `gala.webp`, `gala-card.webp` |
| Conférence | `conference-card.webp` |
| Dîner privé | `private-card.webp` |

### Consignes de génération

- **Réception.** Photorealistic editorial photography for a premium Tunisian event agency web app. Full bleed portrait editorial photograph of a candlelit wedding reception inside a historic Mediterranean villa courtyard. Ivory arches, rows of champagne candles, cream flowers and restrained plum/bordeaux linens, late evening golden side light, rich shadow gradients, exquisite but realistic fabric and table details. Composition center weighted, depth from foreground set table to reception arch, suitable for cropping landscape and portrait. No text, branding, logos, collage or watermark.
- **Gala.** Photorealistic wide editorial photograph for an upscale event management web dashboard. A sophisticated black-tie gala in an airy historic Tunisian venue, banquet tables with candles and warm brass chandeliers, subtle dusty rose and burgundy accents, deep wine shadows, realistic atmospheric light and a clear recognizable elegant celebration scene. Balanced frame, foreground gently textured, center-right luminous focus. Landscape framing, no text, brands or watermark.
- **Conférence.** Photorealistic wide editorial photo for a premium events dashboard, elegant professional conference with empty audience chairs, architectural conference stage lit with warm champagne lights and understated burgundy drapery, subtle Mediterranean architecture. Realistic event venue, centered composition for a small card crop. No text, logos, watermark.
- **Dîner privé.** Photorealistic wide editorial photo as a thumbnail for private parties and celebrations, Mediterranean villa terrace with a beautifully set intimate birthday dinner and dusty rose roses, champagne glassware, hanging lights at dusk and cream linen, no people, warm elegant styling. Clear focal point at center, no text, watermark or logos.

## Vérifications

- `manage.py check` a réussi. `makemigrations --check --dry-run` n’a détecté aucun changement de schéma.
- Les 26 tests Django ont réussi. Ils couvrent les CRUD des six gestions, les validations, les rôles, le calendrier, les exports, les documents et l’authentification.
- Les deux scripts applicatifs passent `node --check`.
- Un navigateur Chrome de test avec Playwright a vérifié les versions 1440, 768, 390 et 320 px sur une base SQLite isolée. Les parcours vérifiés comprennent les pages de compte, la connexion, les listes et formulaires des six modules, la navigation du calendrier, la vue par cartes, la confirmation de document, les graphiques, les pages de paramètres et l’admin. Les captures de la connexion, du dashboard et de la liste des événements ont été examinées. Les principaux écrans testés ne présentaient aucun débordement horizontal de la page. Les grands tableaux gardent leur propre défilement.

## Périmètre et limites

La base de travail, les modèles, les migrations, les vues, les formulaires, les URL et les règles métier ont été préservés. Les tests avec événements illustrés ont utilisé une base indépendante. L’aperçu intégré était indisponible. Le contrôle visuel a été effectué avec Chrome en mode headless. La vérification navigateur est limitée à Chrome et aux tailles testées.
