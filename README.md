# Vertical Science Studio

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
