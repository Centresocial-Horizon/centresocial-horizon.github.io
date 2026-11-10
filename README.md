# Site du Centre social et socioculturel Horizon

Ce dossier est préparé pour le compte **Centresocial-Horizon**, dans le dépôt public
`Centresocial-Horizon.github.io`. L’adresse prévue est
`https://centresocial-horizon.github.io/` ; seule la réussite de la publication
GitHub Pages confirme qu’elle fonctionne.

## Modifier les informations sans coder

Après la connexion initiale, ouvrez `/admin/` sur le site. Connectez-vous, choisissez
une rubrique, remplissez les champs, puis publiez. L’interface permet de gérer
les actualités, les programmes PDF, l’équipe, les horaires, les tarifs, les photos
et les pages. Les contenus et les données de recherche sont reconstruits ensemble.

Le bouton de publication envoie les changements dans ce dépôt. GitHub construit
ensuite la nouvelle version. Attendez la confirmation de réussite avant de
vérifier le site public. En cas d’échec, la dernière version réussie reste en ligne
et le journal de publication indique le problème.

Les actualités et programmes dépassés de plus de deux mois disparaissent de
l’affichage. Une actualisation automatique est prévue chaque jour. Les pages
permanentes ne sont pas masquées à cause de leur ancienne date de création.

## Configuration initiale restant à autoriser

La connexion n’est **pas active** tant que `turbo_site_id` vaut `null` dans
`admin/config.yml`. Aucun faux identifiant, mot de passe ou jeton n’a été placé
dans les fichiers.

Une personne disposant du compte du centre doit autoriser la connexion au dépôt
sur Decap Turbo, choisir son offre **Free**, créer le site relié à ce dépôt et
indiquer l’origine `https://centresocial-horizon.github.io` ainsi que le chemin
`admin/config.yml`. Le véritable identifiant de site fourni par Turbo peut alors
être renseigné. Ce paramètre est public ; les mots de passe et les jetons restent
dans le service de connexion.

Dans GitHub, les réglages **Settings → Pages → Source** doivent utiliser
**GitHub Actions**. Le fichier `.github/workflows/pages.yml` contient déjà les
étapes de vérification et de publication.

## Gratuité et accès

- GitHub Pages fonctionne avec GitHub Free pour ce dépôt public, dans ses limites
  d’utilisation. Le site reste accessible par HTTPS sur l’adresse `.github.io`.
- L’offre gratuite Decap Turbo prévoit un site et un compte éditeur. Plusieurs
  comptes éditeurs indépendants demandent une autre offre ; aucun abonnement
  payant ni essai Pro n’est nécessaire pour cette configuration à un éditeur.
- Les fichiers du dépôt sont publics. N’y ajoutez pas de mots de passe, jetons,
  listes d’adhérents, pièces d’identité ou documents privés.
- La mise en ligne ne transfère pas les e-mails ni l’ancien nom de domaine du
  centre. Leur gestion doit être vérifiée séparément.

Ce dépôt ne contient ni l’historique Git privé du projet de travail, ni les
anciens outils de migration WordPress, ni les paramètres de l’hébergement Sites.

Documentation : [GitHub Pages](https://docs.github.com/fr/pages/getting-started-with-github-pages/what-is-github-pages),
[Decap Turbo](https://decapcms.org/docs/turbo-getting-started/),
[offres Decap Turbo](https://decapcms.org/turbo/).
