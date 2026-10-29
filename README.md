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

Chaque nouvelle vidéo peut désormais recevoir une **narration neuronale anglaise** automatiquement : `--narrate --tts-provider edge` pour un rendu léger, ou `--narrate --tts-provider kokoro` pour une voix ONNX locale. `--voice narration.wav` reste disponible pour une piste personnelle. La musique et les effets sont produits localement ; le fournisseur Edge nécessite une connexion Internet. Le format est strictement **9:16** ; la largeur doit être un multiple de 9.

## Personnalisation

Éditer `presets/paper-to-moon.json` : titre, texte de révélation, épaisseur initiale, nombre de plis, durées de scène et accélération cosmique. Les objets de comparaison (dés, tasse, chat, personne, maison, tour et montagne) sont des vecteurs dessinés avec Pillow dans `studio.py`. Chaque image est calculée à un instant donné puis envoyée immédiatement à FFmpeg : mémoire vidéo constante, rendu reproductible et aucune IA payante.

**Précision scientifique :** une épaisseur de 0,1 mm doublée 42 fois donne environ 439 805 km, soit davantage que la distance moyenne Terre–Lune (384 400 km). Le pliage est purement théorique. Le compteur est calibré en unités réelles ; les illustrations utilisent une caméra cinématique, pas une échelle cartographique stricte.

## Qualité et limites

Le moteur produit un MP4 H.264/AAC avec une musique originale générée localement, une couverture et un manifeste. Les tests vérifient le calcul, la continuité temporelle, l'image, le son et un rendu FFmpeg de bout en bout. Les deux moteurs couvrent maintenant les pliages exponentiels et six types de scènes astronomiques réutilisables ; les autres familles de sciences demanderont des visuels supplémentaires. La synthèse vocale anglaise est intégrée à la génération, avec mise en évidence progressive des sous-titres et adaptation des durées de scènes à la narration. La qualité dépend du moteur vocal choisi et du fonctionnement de son service.

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

Pour un sujet encyclopédique, le système tente une récupération de résumé Wikipédia et conserve son lien. Un texte ou brief détaillé fourni directement par l'utilisateur peut alimenter les scènes. Si aucune preuve n'est disponible, le mode reste **exploratoire**, sans invention de chiffres ou de faits. Le moteur universel constitue une base d'infographies génériques, **pas encore** un système de documentaire automatiquement illustré de manière unique sur chaque thème. Il génère désormais une voix neuronale anglaise et des sous-titres animés. Les 7 familles d'animations sont procédurales et animées image par image ; cela ne signifie pas que chaque sujet dispose d'une reconstitution 3D spécifique.


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

### Dépannage : « Failed deploy » sur Render

La validation Docker indépendante de Render est assurée par [Validate Render Docker deployment](https://github.com/dbrckk/Production-vid-o-verticale-/actions/workflows/docker-smoke.yml). Elle reconstruit l'image de production, démarre le serveur sur le port `10000`, puis vérifie `GET /` et les accès authentifiés / non authentifiés à l'API.

Un service créé avec l'ancienne version de `render.yaml` pouvait démarrer sans `STUDIO_TOKEN`. Dans ce cas, le serveur refuse de s'exposer publiquement et termine avec l'erreur `STUDIO_TOKEN (16 caractères minimum) obligatoire hors localhost`.

**Service Render existant :** dans le dashboard du service → **Environment**, vérifier que `STUDIO_TOKEN` existe et contient au moins 16 caractères (ne jamais publier sa valeur). Sinon, ajouter la variable, puis choisir **Save, rebuild, and deploy**. Le `render.yaml` actuel contient `generateValue: true` pour que **les nouvelles créations** de Blueprint reçoivent automatiquement un secret de 256 bits. La modification du Blueprint ne garantit pas l'ajout rétroactif d'une variable manquante sur un service déjà créé.

Si le jeton est déjà configuré et que le service échoue encore, ouvrir **Deploys → déploiement échoué → Logs** : distinguer **Build failed** (téléchargement d'image, apt/pip, clonage) de **Runtime failed** (exception, port, erreur de processus). Ne pas supprimer ou recréer le service sans connaître l'erreur. Vérifier aussi que **Runtime = Docker**, **Branch = main**, **Port = 10000** (le Dockerfile et `webapp.py` le définissent déjà).


## English Neural Narration + Kinetic Motion

**New output standard:** English-only source research, English headlines and captions, neural voiceover, dynamic word highlights, and 9:16 MP4 with AAC audio.

**True motion, not slide transitions.** The `kinetic.py` engine renders new geometry at every timestamp: ocean wave phase and swimming fish, volcanic lava and ballistic particles, orbiting planets and moons, pulsing circuits, an animated heartbeat and ECG, expanding financial charts, and a continuously moving causal diagram for other categories. Scenes keep moving between cuts.

**Voice choices.** On the small Render web service, Edge Neural (`en-US-AriaNeural`) produces English voiceover without a paid API key. It requires a working external service; if synthesis fails, the job explicitly reports an error rather than silently outputting a music-only slideshow. On GitHub Actions, `voice_provider=kokoro` uses the permissively licensed [Kokoro ONNX](https://github.com/thewh1teagle/kokoro-onnx) model. Its weight files are downloaded and cached **only when a manually dispatched video uses Kokoro**. Use `voice_provider=edge` to save bandwidth. The one-minute GitHub smoke test verifies actual Edge speech audio on the exact production Docker image.

Commands:

```bash
# Install ffmpeg + fonts first; Python dependencies are in requirements.txt.
python generate_topic.py --topic "How do ocean currents shape the climate?" --output output/story.json
python studio.py --config output/story.json --output output/science.mp4 --narrate --tts-provider edge --width 1080 --fps 30

# Optional: install requirements-voice.txt and download official Kokoro model
# and voices into models/, then use --tts-provider kokoro
```

The JSON manifest stores voice information, per-word approximate subtitle timings and source citations. **Subtitle timing:** Edge Neural provides actual word-boundary metadata, which drives word-by-word highlighted subtitles. Kokoro ONNX uses a clearly identified estimated timing fallback until a local forced-aligner is integrated. Scientific validity depends on the underlying sources: arbitrary unsourced prompts are exploratory, not independent fact-checked documentaries. The generic animation category cannot yet recreate every possible real-world event faithfully.



## English motion-documentary engine (2026-10-29)

The public Render interface runs **English only**, offers three neural narrator voices
(Andrew US, Aria US, Ryan UK), and produces MP4 files with real animated vector motion
and spoken-word subtitle timings. A missing voice stream is an error, not silent video.
Transient neural voice service outages are retried up to three times. The music bed is
lowered underneath speech, with compression and an output limiter.

**Evidence-backed story direction**

- For eight narrowly recognized scientific subjects (ocean currents, ocean tides,
  volcanic eruptions, photosynthesis, the solar system, heartbeats, earthquakes and
  meteorology), the `editorial.py` script supplies six distinct English explanatory
  beats. This is documented science content, **not** an AI claim to know any subject.
- News stories only narrate information present in the article headline/summary plus
  the named source and publication date. Thin RSS reports are rejected; enough
  information for three beats does not get padded with six generic slides.
- For other topics with usable English Wikipedia context, the script dynamically uses
  the available evidence to produce the number of meaningful scenes supported by it.
  Unverified subjects may still remain exploratory.
- `kinetic.py` implements time-continuous diagrams; the six earthquake scenes now
  separately depict drifting plates, accumulating stress, sudden slip, propagating
  seismic waves, site response, and a moving seismometer trace.
- `tests/test_editorial_motion.py` checks physical movement and scene-to-scene visual
  differentiation; neural integration tests cover English voice audio and word timing.

**Download playable quality proofs** from GitHub Actions (log in to GitHub to access
the artifacts):
[Ocean currents + English narration](https://github.com/dbrckk/Production-vid-o-verticale-/actions/workflows/ocean-proof.yml) ·
[Earthquake documentary + English narration](https://github.com/dbrckk/Production-vid-o-verticale-/actions/workflows/earthquake-proof.yml).

For a finished **Full HD 1080 × 1920** video, use the main
[Render vertical science video workflow](https://github.com/dbrckk/Production-vid-o-verticale-/actions/workflows/render.yml)
with `mode=custom`, `quality=1080p` and `voice_provider=kokoro` (offline).
The Render free instance uses lighter Edge neural voices for its interactive UI,
and available CPU/RAM and storage limits apply.

**Visual limitation:** physical vector animation and narration have replaced the
static-card slideshow for supported subjects, but this is not yet automatic
photorealistic cinematic footage for any arbitrary topic. Realistic assets,
subject-specific 3D simulation and editorial verification still require
further work.

## Cinematic 2D production quality (English only)

Production uses procedural **animated 2D illustrations**, never static slides or
a mandatory 3D engine. The edited scene layers are handled by `cinematic.py`:
camera push/pull, eased 380-ms art dissolves and separate motion-safe captions.
Curated science subjects retain their specific physics diagrams; arbitrary
source-backed stories use six distinct and data-honest visual treatments from
`semantic_motion.py` rather than overlays of unrelated charts.

**English narration:** `en-US-AndrewNeural` via Edge is the default on Render
and GitHub Actions. Its actual provider word boundaries drive stable, large
two-to-three-word English captions (`subtitle_design.py`). Other authorized
English narrators remain selectable from the mobile UI; Kokoro ONNX remains
an optional offline GitHub alternative with estimated word timings.

**Sound:** the `soundscape.py` score uses original, locally synthesized
ambient music with scene cues; `audio_mastering.py` applies dialogue-triggered
music ducking, voice dynamics and a mobile-focused target near -17 LUFS.
Deliverables use H.264 and AAC 48 kHz with the exact 9:16 aspect ratio.

**Mandatory checks:** `qa_video.py` runs after narration and rendering,
before the Render service marks a job ready and before GitHub manual exports.
It rejects missing or unsynchronized voice, wrong video/audio formats, loudness
outside the accepted range, and nearly static visuals. Its inspectable JSON
report includes integrated loudness, true peak, narration word count,
sampled animation activity and video dimensions.

Run on an existing generated output:

```bash
python qa_video.py --video output/science.mp4 \
  --manifest output/science.json --report output/quality.json
```

A passing technical QA report **does not guarantee** that an arbitrary topic
is factually complete, that the artwork is aesthetically premium, or that
a synthetic voice is indistinguishable from a human narrator. Unsupported
news remains source-constrained and thin reports are rejected rather than
filled with invented events or statistics. GitHub tests and production Docker
smoke checks must pass before considering a code revision ready.


## Social publishing profile — clean 1080p master

The **Publish** option in the Render mobile interface is selected by default:
1080 × 1920 (exact 9:16), 30 FPS, H.264 **High** (`libx264` slow preset,
CRF 16, 2-second GOP), limited-range YUV420p with explicit **BT.709** color
primaries / transfer / matrix, faststart MP4, and AAC LC at 48 kHz / 256 kbit/s.
The mastering filter targets about **−17 LUFS** and automatically ducks the
original music under English narration. Lower-resolution modes are clearly
marked **Review**, not publication masters.

**Clean social layout:** the delivery image intentionally contains no
`01/06` or other chapter counter, no studio branding label, no watermark,
no playback progress bar and no extraneous end-card. Word-timed subtitles
stay within the horizontal phone-safe area, with the bottom **170 reference
pixels (about 16.6% of the full vertical image)** left clear for social-app
controls and captions. Paper-fold metrics remain when they actually explain
the science, but unrelated bottom footers were removed. The storyboard,
universal and classic paper formats all support English narrated subtitles.

To validate the complete publication pipeline, run the GitHub workflow:
[Publish-grade 1080p English documentary proof](https://github.com/dbrckk/Production-vid-o-verticale-/actions/workflows/publication-proof.yml).
It renders a complete English-voice documentary in full HD and blocks the
export unless the format, color tags, motion, word cues and audio pass the
QA gate. The generated `publication-quality.json` records the objective
measurements. A passing technical report does not substitute for a human
editorial and factual review before actually posting on a social network.

## 2026 cinematic 2D: 60 FPS and one-take English narration

- **Smoother real motion:** 1080 × 1920 H.264, 60 distinct frames per second and
  2-second GOP; the 30fps mode remains available to conserve Render free-tier
  CPU resources. GitHub Actions defaults to 1080p60 for manual exports.
- **Stronger original artwork:** tectonic cross-sections use animated layered
  sediments, mineral grain, geological fault highlights and detailed facades.
  The rupture moves once and relaxes with damped aftershocks; cinematic framing
  brings the actual explanatory diagrams closer rather than enlarging the UI.
- **More natural English voice:** Microsoft Brian Multilingual is the default
  narrator after a successful real proof render. Edge narration runs as one
  continuous passage with the provider's word boundaries, eliminating abrupt
  joins between six independently spoken scenes. A timing-aware fallback
  remains in place when the provider's word metadata is incomplete.
- **Sound remains balanced:** voice-sidechain music ducking, a near −17 LUFS
  mobile mix and 48kHz AAC remain required by the finished-video QA gate.
- **Clean presentation:** all three visual modes remove scene counters,
  slide numbering and watermarks, with captions in social-safe margins.

**Rights before monetization.** The official Microsoft Q&A moderation response
in June 2026 says that no public document explicitly clarifies commercial
rights for Edge Read Aloud / edge-tts output. Do not assume Edge-generated
speech is cleared for monetized redistribution merely because it is accessible.
Microsoft support can clarify a particular use; a licensed commercial TTS
provider is another option. The optional local Kokoro model's *weights* carry
an Apache-2.0 licence (see the model card), although publishing remains subject
to any other applicable rights. See:
- https://learn.microsoft.com/en-us/answers/questions/5925556/commercial-use-of-edge-read-aloud-voices-via-edge
- https://huggingface.co/hexgrad/Kokoro-82M

