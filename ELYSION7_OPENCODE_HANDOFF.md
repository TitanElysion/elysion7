# Elysion7 — Handoff / Instructions pour OpenCode

## 1. Mission

Tu travailles sur **Elysion7**, un moteur local de documentation inspiré de Context7.

Objectif : construire une alternative locale, gratuite et open source capable de :
1. récupérer des dépôts/documentations ;
2. analyser et nettoyer les fichiers ;
3. conserver les métadonnées de provenance et de version ;
4. découper les documents en chunks ;
5. générer des embeddings localement ;
6. indexer dans Qdrant ;
7. effectuer une recherche hybride (lexicale + vectorielle, puis reranking si pertinent) ;
8. exposer les résultats via FastAPI ;
9. exposer ensuite l'API via MCP pour des agents IA locaux.

Architecture cible :

GitHub / docs
    ↓
clone/update
    ↓
scanner
    ↓
parser
    ↓
classification / nettoyage
    ↓
chunker
    ↓
embeddings
    ↓
Qdrant
    ↓
recherche hybride + reranking
    ↓
FastAPI
    ↓
MCP
    ↓
IA locale

## 2. Règle importante

NE PAS refaire l'architecture à chaque étape.

Le projet a déjà été réfléchi et plusieurs composants fonctionnent.
Avant de modifier quelque chose :
- inspecter l'existant ;
- réutiliser le code existant ;
- faire la modification minimale nécessaire ;
- tester ;
- continuer vers l'étape suivante.

Ne pas introduire de dépendance lourde sans nécessité.
La priorité est : gratuit, local, open source et raisonnable en ressources.

## 3. Répertoire

Projet :

~/Storage/Elysion7

Structure actuelle :

Elysion7/
├── api/
├── backups/
├── config/
├── data/
│   ├── cache/
│   ├── documents/
│   ├── qdrant/
│   └── repos/
├── ingestion/
├── mcp/
└── models/

Environnement Python :

~/Storage/Elysion7/.venv

Dépendances déjà installées :

- pyyaml
- gitpython
- pathspec
- markdown
- beautifulsoup4
- fastapi
- uvicorn

## 4. Sources prévues

Bibliothèques initialement prévues :

1. n8n
2. Docker
3. Python
4. FastAPI
5. Django
6. Node.js
7. TypeScript
8. llama.cpp
9. Qdrant
10. MCP
11. PostgreSQL
12. React
13. Next.js
14. Proxmox
15. Linux
16. Flutter
17. HTML
18. CSS
19. PHP
20. W3C
21. Telegram
22. Discord
23. WhatsApp

La configuration est dans :

config/libraries.yaml

Elle doit rester la source de configuration des bibliothèques.

## 5. État actuel

### Qdrant

Qdrant fonctionne déjà via Docker.

Conteneur :

elysion7-qdrant

Ports actuels :

6333
6334

Stockage :

data/qdrant

Image utilisée :

qdrant/qdrant:latest

Version observée :

1.19.1

### FastAPI

Dépôt :

data/repos/fastapi

Repository :

https://github.com/fastapi/fastapi.git

Branche :

master

Le dépôt a initialement été cloné en shallow clone, puis rendu complet avec :

git fetch --unshallow --tags

La commande a nécessité plusieurs tentatives à cause d'une mauvaise connexion, mais la seconde tentative a réussi.

Le dépôt possède :

305 tags

Tag stable récent observé :

0.141.1

Commit actuellement indexé :

50113da16fec53b66b80d75e80a89296de4fa5a5

git describe :

0.141.1-106-g50113da16

Donc le commit actuel est 106 commits après 0.141.1 et correspond à un état de développement de master, pas à une release stable.

## 6. Scanner actuel

Fichier :

ingestion/scanner.py

Le scanner :
- charge config/libraries.yaml ;
- applique include/exclude ;
- parcourt le dépôt ;
- retourne les fichiers sélectionnés.

Pour FastAPI, le dernier résultat validé était :

2198 fichiers sélectionnés

Répartition :

documentation : 1665
source : 526
test : 7

## 7. Parser actuel

Fichier :

ingestion/parser.py

Fonctions principales :

- detect_language()
- read_file()
- clean_markdown()
- extract_title()
- extract_sections()
- should_ignore_section()
- parse_file()

Langages actuellement reconnus notamment :
markdown, mdx, rst, python, typescript, tsx, javascript, jsx, json, yaml, html, css.

Le parser ignore notamment certaines sections de sponsoring.

## 8. Chunker actuel

Fichier :

ingestion/chunker.py

Valeurs actuelles :

DEFAULT_CHUNK_SIZE = 1200
DEFAULT_OVERLAP = 150
MIN_CHUNK_SIZE = 80

Le chunker tente de couper préférentiellement :
1. sur double saut de ligne ;
2. puis saut de ligne ;
3. puis espace.

Statistiques validées sur FastAPI :

Documents générés : 15452
Chunks générés : 13560

Minimum : 80 caractères
Maximum : 1200 caractères
Moyenne : 444.9 caractères
Médiane : 381 caractères

Chunks par catégorie :

documentation : 13191 (97.3%)
source : 365 (2.7%)
test : 4

Petits chunks <150 caractères :

1628

Ces valeurs sont acceptées pour la V1.
Ne pas refaire le chunker sans raison concrète.

## 9. Classification

Le pipeline classe actuellement les fichiers en :

- documentation
- example
- source
- test
- other

Priorités :

documentation = 3
example = 2
source = 1
test = 0

Le code de priorité se trouve dans :

ingestion/metadata.py

## 10. Métadonnées Git

Fichier :

ingestion/metadata.py

Le module doit conserver au minimum :

- repository
- branch
- commit
- commit_short
- commit_date
- version
- version_type
- tag
- nearest_tag
- commits_since_tag

Le comportement souhaité est :

### Release exacte

Si HEAD correspond exactement à un tag :

version = tag
version_type = stable

### Développement après une release

Si HEAD est après un tag :

version = <tag>+<nombre_de_commits>

Exemple :

0.141.1+106

version_type = development

### Aucun tag exploitable

version = unknown
version_type = unknown

IMPORTANT :
La version ne doit jamais remplacer le commit exact.
Le commit reste la référence de provenance absolue.

## 11. Prochaine étape immédiate

La prochaine étape du projet est :

### A. Valider metadata.py

Tester :

python - <<'PY'
from pathlib import Path
from ingestion.metadata import get_git_metadata

data = get_git_metadata(Path("data/repos/fastapi"))

for key, value in data.items():
    print(f"{key:20} : {value}")
PY

Le résultat attendu doit notamment montrer :

version              : 0.141.1+106
version_type         : development
nearest_tag          : 0.141.1
commits_since_tag    : 106

### B. Construire le manifest

Créer ensuite un manifest par bibliothèque.

Exemple :

data/documents/fastapi/manifest.json

Structure minimale :

{
  "library": "fastapi",
  "name": "FastAPI",
  "repository": "https://github.com/fastapi/fastapi.git",
  "branch": "master",
  "commit": "...",
  "version": "0.141.1+106",
  "version_type": "development",
  "indexed_at": "...",
  "documents": 15452,
  "chunks": 13560
}

Le manifest doit devenir la source de vérité de l'état du corpus indexé.

NE PAS générer d'embeddings avant que cette étape soit validée.

## 12. Étapes suivantes

Après le manifest :

1. finaliser le modèle de données des chunks ;
2. choisir un modèle d'embedding local adapté au matériel disponible ;
3. créer la collection Qdrant ;
4. indexer les chunks ;
5. tester la recherche vectorielle ;
6. ajouter la recherche lexicale ;
7. combiner lexical + vectoriel ;
8. ajouter un reranker seulement si nécessaire ;
9. construire FastAPI ;
10. construire MCP ;
11. ajouter la gestion des mises à jour de bibliothèques.

## 13. Modèle de chunk

Chaque chunk doit conserver sa provenance.

Champs attendus :

- library
- version
- repository
- branch
- commit
- commit_date
- source
- path
- language
- title
- section
- category
- priority
- chunk_index
- content

Ne jamais indexer un chunk sans pouvoir retrouver son fichier source.

## 14. Contraintes matérielles et philosophiques

Le projet est développé localement.

Priorités :

1. 100 % gratuit ;
2. open source quand possible ;
3. local ;
4. faible consommation RAM/disque ;
5. simplicité ;
6. reproductibilité ;
7. provenance précise.

Ne pas proposer une architecture SaaS ou une API payante comme dépendance obligatoire.

Le système doit pouvoir fonctionner avec les modèles IA locaux de l'utilisateur.

## 15. Gestion Git

Le dépôt FastAPI est maintenant complet.

Pour les futures bibliothèques, éviter de télécharger inutilement tout l'historique si ce n'est pas nécessaire.

Le système devra à terme pouvoir :
- récupérer la branche courante ;
- détecter les tags ;
- déterminer la version stable la plus récente ;
- conserver le commit exact ;
- mettre à jour le dépôt ;
- détecter si le corpus doit être réindexé.

Ne pas implémenter toute cette automatisation maintenant.
Commencer par le manifest et l'indexation.

## 16. Style de travail attendu

L'utilisateur préfère travailler rapidement et concrètement.

Donc :

- expliquer brièvement ce qui est fait ;
- donner les commandes exactes ;
- éviter les détours ;
- ne pas multiplier les refontes ;
- ne pas demander une validation pour chaque micro-décision ;
- tester après chaque changement significatif ;
- si une décision est raisonnable, la prendre et avancer.

Quand plusieurs solutions sont possibles, choisir la plus simple qui respecte les contraintes.

## 17. Première instruction à OpenCode

Commence par inspecter le dépôt Elysion7.

Ne modifie rien immédiatement.

Vérifie :

- structure du projet ;
- ingestion/metadata.py ;
- ingestion/analyze_repository.py ;
- ingestion/scanner.py ;
- ingestion/parser.py ;
- ingestion/chunker.py ;
- config/libraries.yaml ;
- état Git de data/repos/fastapi.

Puis résume en quelques lignes :

1. ce qui existe réellement ;
2. ce qui est déjà fonctionnel ;
3. ce qui manque pour terminer le manifest ;
4. la modification minimale nécessaire.

Ensuite seulement, implémente la prochaine étape.

## 18. Important pour la collaboration avec ChatGPT

ChatGPT a déjà accompagné la conception d'Elysion7.

OpenCode devient maintenant l'agent local chargé de travailler directement dans :

~/Storage/Elysion7

ChatGPT reste utilisé pour :
- architecture ;
- décisions importantes ;
- recherche ;
- conception ;
- résolution de problèmes complexes ;
- revue des changements.

OpenCode est utilisé pour :
- lire le dépôt ;
- modifier les fichiers ;
- lancer les tests ;
- exécuter les commandes ;
- itérer rapidement.

Toujours préserver l'état fonctionnel existant.

---

# FIN DU HANDOFF
