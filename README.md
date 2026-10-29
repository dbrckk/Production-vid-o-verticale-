# Vertical Science Studio

## Déployer en un clic sur Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/dbrckk/Production-vid-o-verticale-)

En cas de connexion Render indisponible dans ChatGPT, le bouton ouvre directement la création du service à partir du `render.yaml` déjà inclus. **Sélectionner le bon compte Render avant de valider**, choisir le plan **Free** et saisir un secret personnel aléatoire d'au moins 16 caractères pour `STUDIO_TOKEN` (à conserver dans votre gestionnaire de mots de passe). Ne pas communiquer ce secret dans un dépôt, une issue ou une capture publique. Le service sera créé sur le compte effectivement sélectionné ; cette procédure n'est pas une migration des anciens services.

Générateur de vidéos scientifiques néon **9:16**, hors ligne, créé pour reproduire le langage visuel des vidéos à progression exponentielle : compteur dynamique, silhouettes vectorielles, croissance du papier, zoom Terre/Lune, orbites, halos, particules spatiales et musique/effets originaux synchronisés. Le projet utilise des illustrations procédurales originales et non des images copiées d'une vidéo ou des logos de plateformes.

## Deux modes de création (sans clé API)

| Modèle | Preset | Résultat |
|---|---|---|
| **Voyage exponentiel** | `presets/paper-to-moon.json` | Progression des plis, comparaisons de dimensions, Terre/Lune et espace |
| **Storyboard astronomique** | `presets/sun-vanished.json` | Six scènes : Soleil, propagation lumineuse, délai, orbite, refroidissement, galaxie |

Le **mode storyboard** se pilote par JSON : chaque scène définit `start`, `end`, `headline`, `caption`, `metric` (facultatif) et `visual`. Les visuels procéduraux disponibles sont `sun`, `light_path`, `countdown`, `orbit`, `ice` et `galaxy`. Les scènes couvrent la durée de la vidéo, sans lacunes ni chevauchements ; le validateur refuse les scénarios incohérents. Les transitions sont fondues, les sous-titres sont mesurés pour respecter les marges mobiles, et les changements de scène déclenchent des sons originaux. Le scénario sur le Soleil est une expérience de pensée, non une prédiction possible de son évolution physique.

```bash
python studio.py --config presets/sun-vanished.json --output output/sun.mp4 --width 1080 --fps 30
python studio.py --config presets/paper-to-moon.json --output output/paper.mp4 --width 1080 --fps 30
```

Pour créer un autre sujet, duplique le preset `sun-vanished.json`, change les titres, textes, durées et les types de visuels ; le moteur conserve la composition 9:16, les halos, la timeline et l'export audio/vidéo. Les scènes utilisent actuellement des modèles **astronomiques** : un sujet non astronomique demandera de nouveaux visuels spécifiques, pas uniquement un changement de textes.

## Utilisation depuis Android (sans ordinateur)

1. Ouvrir **Actions → Render vertical science video → Run workflow** dans ce dépôt.
2. Choisir le sujet `sun-vanished` ou `paper-to-moon`, puis `1080p`, `720p` ou `preview`. Le titre personnalisé modifie l'ouverture du modèle sélectionné.
3. Ouvrir l'exécution terminée et télécharger l'artefact `vertical-science-...` : il contient `science.mp4`, `cover.png` et `science.json`.

À chaque push sur `main`, GitHub exécute uniquement les tests et un court rendu de vérification. Le rendu complet 1080p ne démarre que sur demande manuelle, pour économiser les minutes GitHub Actions. Il utilise uniquement GitHub Actions, Python, Pillow, NumPy et FFmpeg. Les minutes GitHub Actions restent soumises aux limites de votre compte.

## En local ou sur serveur

```bash
sudo apt-get install -y ffmpeg fonts-dejavu-core
python3 -m pip install -r requirements.txt
python3 -m pytest tests/ -q
python3 studio.py --config presets/paper-to-moon.json --output output/science.mp4 --width 1080 --fps 30
```

Pour un rendu de vérification rapide :

```bash
python3 studio.py --width 540 --fps 15 --duration 8 --preview --output output/preview.mp4
```

Pour ajouter une narration dont vous possédez les droits : `--voice narration.wav` (mixage avec la musique originale). Le son synthétique fonctionne sans clé ni fournisseur externe. Le format est strictement **9:16** ; la largeur doit être un multiple de 9.

## Personnalisation

Éditer `presets/paper-to-moon.json` : titre, texte de révélation, épaisseur initiale, nombre de plis, durées de scène et accélération cosmique. Les objets de comparaison (dés, tasse, chat, personne, maison, tour et montagne) sont des vecteurs dessinés avec Pillow dans `studio.py`. Chaque image est calculée à un instant donné puis envoyée immédiatement à FFmpeg : mémoire vidéo constante, rendu reproductible et aucune IA payante.

**Précision scientifique :** une épaisseur de 0,1 mm doublée 42 fois donne environ 439 805 km, soit davantage que la distance moyenne Terre–Lune (384 400 km). Le pliage est purement théorique. Le compteur est calibré en unités réelles ; les illustrations utilisent une caméra cinématique, pas une échelle cartographique stricte.

## Qualité et limites

Le moteur produit un MP4 H.264/AAC avec une musique originale générée localement, une couverture et un manifeste. Les tests vérifient le calcul, la continuité temporelle, l'image, le son et un rendu FFmpeg de bout en bout. Les deux moteurs couvrent maintenant les pliages exponentiels et six types de scènes astronomiques réutilisables ; les autres familles de sciences demanderont des visuels supplémentaires. La synthèse vocale automatique n'est pas intégrée : une piste de narration existante peut être ajoutée via `--voice`.

## Moteur universel : n'importe quel sujet, actualités et éditeur Android

Un troisième mode **universal** génère un storyboard vertical original avec six visualisations animées : ouverture lumineuse, globe, chronologie, réseau, comparaison et conclusion. Il ne dépend d'aucun service d'IA payant. Il est compatible avec les deux anciens modèles du dépôt.

### Depuis GitHub Actions sur Android (aucun serveur nécessaire)

Ouvrir [Render vertical science video](https://github.com/dbrckk/Production-vid-o-verticale-/actions/workflows/render.yml), puis **Run workflow** :
- **mode = custom** : saisir \`custom_topic\` (ex. « Pourquoi la mer est salée ? »), puis choisir \`quality\`.
- **mode = random_news** : sélectionner automatiquement une actualité importante et récente parmi les flux disponibles ; les sources sont conservées dans \`science.json\`. Le workflow échoue explicitement si les flux ne renvoient aucune actualité fraîche.
- **mode = preset** : choisir \`subject = sun-vanished\` ou \`paper-to-moon\`.

Le fichier vidéo, la couverture et les métadonnées sont déposés dans les artefacts de l'exécution. La génération complète ne se déclenche **pas** automatiquement à chaque push : les pushes exécutent seulement les tests.

### Interface mobile avec bouton « Actualité importante au hasard »

Sur une machine avec Python 3.11+, Pillow, NumPy, FFmpeg et les polices DejaVu :

\`\`\`bash
pip install -r requirements.txt
python webapp.py
\`\`\`

Ouvrir \`http://127.0.0.1:8765\`. L'interface propose un champ sujet libre, un bouton **Actualité importante au hasard**, un choix de résolution, un bouton **Créer la vidéo** et un lecteur avec téléchargement MP4.

Pour exposer l'interface depuis un serveur distant, définir un mot de passe/token long de 16 caractères minimum via \`STUDIO_TOKEN\`. Par exemple dans la configuration secrète de l'hébergeur, **jamais dans Git**. Démarrer \`python webapp.py --host 0.0.0.0 --port 10000\`, avec HTTPS devant le service. Le Dockerfile permet une installation sur Render ou tout hébergeur acceptant Docker. **Le dépôt ne déploie pas automatiquement un service public.** La sortie locale est éphémère et conserve au maximum les cinq derniers rendus.

### Génération libre par ligne de commande

\`\`\`bash
python generate_topic.py --topic "Comment fonctionnent les volcans ?" --output output/topic.json
python studio.py --config output/topic.json --width 1080 --fps 30 --output output/science.mp4

# Sélection pondérée parmi les actualités publiées depuis moins de 72 heures
python generate_topic.py --random-news --output output/topic.json
python studio.py --config output/topic.json --width 1080 --fps 30 --output output/news.mp4
\`\`\`

### Fiabilité éditoriale

Les sujets d'actualité sont tirés de flux RSS fixes (franceinfo, France 24, Le Monde, BBC et Guardian), dédoublonnés, filtrés par **date de publication** (72 h), classés par fraîcheur et indices d'importance, puis tirés au sort parmi les sujets les mieux classés. Les sources francophones sont privilégiées. Le classement est **heuristique** : il n'est pas une validation journalistique indépendante de chaque information.

Pour un sujet encyclopédique, le système tente une récupération de résumé Wikipédia et conserve son lien. Un texte ou brief détaillé fourni directement par l'utilisateur peut alimenter les scènes. Si aucune preuve n'est disponible, le mode reste **exploratoire**, sans invention de chiffres ou de faits. Le moteur universel constitue une base d'infographies génériques, **pas encore** un système de documentaire automatiquement illustré de manière unique sur chaque thème. Il n'ajoute pas encore automatiquement de voix naturelle : la piste \`--voice\` existante permet d'intégrer une narration produite séparément.


### Publication de l'interface sur Render (facultative)

Un \`render.yaml\` officiel prépare un service Docker sur le plan \`free\` (sous réserve d'éligibilité et des quotas Render), région Francfort, avec déploiement seulement après réussite des tests GitHub Actions. Pour l'activer, importer ce dépôt comme **Blueprint** dans l'espace Render autorisé et saisir \`STUDIO_TOKEN\` comme secret (16 caractères minimum). Aucun jeton n'est présent dans le dépôt. Après déploiement, le site fournit les boutons de génération et de sélection d'actualités directement depuis Android. Le service utilise un stockage temporaire et ne promet pas de conserver les MP4 après redémarrage.

### Sécurité et coûts

- Application locale par défaut ; un serveur accessible publiquement exige \`STUDIO_TOKEN\` et HTTPS.
- Une seule vidéo en cours à la fois ; contrôle de la qualité, du format et de la taille des requêtes ; nettoyage des anciens MP4.
- Aucun téléchargement d'images depuis des adresses soumises par l'utilisateur. Les actualités proviennent uniquement d'une liste fixe de flux. Les vidéos contiennent des graphismes procéduraux originaux.
- GitHub Actions et hébergement gratuit éventuel soumis aux quotas et conditions du compte. Un rendu 1080p de 30 s peut être lourd en ressources ; préférer \`preview\` pour un essai.



## Hébergement sans abonnement : Hugging Face Static Space + GitHub Actions

Le code de l'interface mobile est dans `hf_space/` (HTML, CSS, JavaScript, pas de backend Python). Cette version utilise un **Static Space**, car Hugging Face exige actuellement un abonnement pour créer de nouveaux Spaces Docker/Gradio sur CPU Basic. Les Static Spaces restent gratuits.

### Mise en service (compte Hugging Face Dbrzck)

1. Sur https://huggingface.co/new-space, créer un Space nommé **vertical-science-studio** sous **Dbrzck**, avec **SDK: Static HTML**. Choisir Public (le contenu du site sera public ; les jetons ne doivent jamais figurer dans le dépôt ou dans l'interface).
2. Sur https://huggingface.co/settings/tokens, créer un **fine-grained access token** autorisant l'écriture sur **Dbrzck/vertical-science-studio** uniquement.
3. Sur https://github.com/dbrckk/Production-vid-o-verticale-/settings/secrets/actions, créer un secret de dépôt nommé **HF_TOKEN** contenant ce jeton.
4. Lancer une fois [Publish static studio to Hugging Face](https://github.com/dbrckk/Production-vid-o-verticale-/actions/workflows/publish-hf.yml) avec « Run workflow ». Les changements du dossier `hf_space/` seront ensuite synchronisés automatiquement. Le workflow refuse silencieusement la publication si le secret est absent et explique ce manque dans les logs.

Le site sera accessible sur **https://huggingface.co/spaces/Dbrzck/vertical-science-studio** après création et publication effective. Ne pas considérer cette URL comme opérationnelle avant un premier déploiement réussi.

### Utilisation du site

- Saisir un sujet libre, ou cliquer sur **Choisir une actualité importante au hasard** : le site utilise `hf_space/news.json`, régénéré par le workflow [Update verified news selection](https://github.com/dbrckk/Production-vid-o-verticale-/actions/workflows/refresh-news.yml) toutes les huit heures. Les articles de plus de 72 heures ne sont jamais proposés par l'interface. S'il n'y a pas d'article récent, la sélection échoue explicitement, sans inventer une actualité.
- Choisir Preview, 720p ou 1080p, puis **Créer la vidéo**. Par défaut, l'interface prépare la valeur à copier et ouvre le workflow GitHub Actions ; aucune autorisation supplémentaire n'est nécessaire.
- Pour lancer un rendu directement depuis le navigateur, saisir facultativement un **GitHub fine-grained personal access token** limité au seul dépôt, avec permission **Actions: read and write**. Le jeton est envoyé **uniquement** à `api.github.com` et n'est jamais enregistré (ni en localStorage ni sur Hugging Face) ; il est effacé de la zone de saisie après le déclenchement accepté. GitHub Actions exécute le rendu et livre l'artefact MP4.
- Le mode `article_url` du workflow prend en charge exactement l'actualité choisie, en vérifiant à nouveau que son URL figure dans les flux RSS récents. Les autres modes `custom`, `random_news` et `preset` restent disponibles.

**Limites explicites :** l'interface statique ne peut pas exécuter directement Python/FFmpeg ni conserver des travaux sur serveur. Le rendu a lieu sur GitHub ; la récupération du MP4 s'effectue depuis les artefacts GitHub Actions. Une source RSS fraîche indique l'origine de l'information, mais ne remplace pas une vérification éditoriale indépendante. Les thèmes libres restent des animations procédurales générées par le moteur actuel et ne sont pas des reportages garantis factuels sans sources.
