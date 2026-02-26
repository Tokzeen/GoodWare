# 🛡️ GoodWare — C2 Pédagogique en Environnement Isolé

> **Démo pédagogique** de sécurité offensive montrant les concepts d'un framework C2 (Command & Control) léger.  
> Usage **strictement réservé** à des environnements isolés, légaux et contrôlés (lab, pentest interne, formation).

---

## 📌 À propos

**GoodWare** est un C2 minimaliste inspiré des frameworks professionnels comme Cobalt Strike ou Sliver.  
Il permet de déployer, gérer et commander des **agents (beacons)** sur des machines cibles depuis une interface centralisée.

Ce projet est un **PoC (Proof of Concept)** à but éducatif pour comprendre :
- Le fonctionnement d'un C2 moderne
- La communication agent ↔ serveur (polling/check-in)
- Les mécanismes de contrôle à distance en environnement air-gapped

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Machines Cibles                       │
│                                                          │
│   [Beacon A]  [Beacon B]  [Beacon C]                    │
│       │            │           │                        │
│       └────────────┴─────polling/check-in────────┐      │
└──────────────────────────────────────────────────┼──────┘
                                                   │
                                    ┌──────────────▼───────────────┐
                                    │         Serveur C2            │
                                    │                               │
                                    │  ┌──────────────────────┐    │
                                    │  │     flask_api         │    │
                                    │  │  (Orchestrateur C2)   │    │
                                    │  │  - Déploiement agents │    │
                                    │  │  - Gestion des tâches │    │
                                    │  │  - Contrôle beacons   │    │
                                    │  └──────────┬───────────┘    │
                                    │             │                 │
                                    │  ┌──────────▼───────────┐    │
                                    │  │    flask_file         │    │
                                    │  │  (Dépôt de payloads)  │    │
                                    │  │  - Stockage beacons   │    │
                                    │  │  - Distribution files │    │
                                    │  └──────────────────────┘    │
                                    └───────────────────────────────┘
                                                   ▲
                                                   │
                                            [Opérateur]
```

---

## 📂 Structure du projet

```
GoodWare/
├── flask_api/          # Serveur C2 principal — orchestration des agents
│   ├── app.py          # API REST de contrôle
│   ├── models.py       # Modèles agents / tâches
│   └── ...
│
├── flask_file/         # Serveur de fichiers — stockage & distribution des beacons
│   ├── app.py
│   └── ...
│
└── README.md
```

---

## ⚙️ Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| 🚀 **Déploiement** | Envoyer un beacon sur une machine cible |
| 📡 **Check-in / Heartbeat** | Les agents reportent leur statut au C2 |
| 🛑 **Stop agent** | Arrêter proprement un beacon distant |
| ⌨️ **Block keyboard** | Bloquer les inputs clavier sur la cible |
| 📁 **File store** | Stocker et servir les payloads/beacons |
| 📋 **Inventaire** | Lister tous les agents actifs et leur statut |

---

## 🚀 Démarrage rapide

### Prérequis

- Python 3.10+
- Docker & Docker Compose (recommandé)

### Lancer avec Docker

```bash
git clone https://github.com/Tokzeen/GoodWare.git
cd GoodWare

# Démarrer le serveur de fichiers et l'API C2
docker compose up --build
```

### Lancer manuellement

```bash
# Terminal 1 — Serveur de fichiers
cd flask_file
pip install -r requirements.txt
python app.py

# Terminal 2 — API C2
cd flask_api
pip install -r requirements.txt
python app.py
```

---

## 🔌 API — Endpoints principaux

### `flask_api` (C2 Controller)

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/agents` | Lister les agents actifs |
| `POST` | `/agents/deploy` | Déployer un beacon sur une cible |
| `POST` | `/agents/<id>/stop` | Stopper un agent |
| `POST` | `/agents/<id>/block_keyboard` | Bloquer le clavier |
| `GET` | `/agents/<id>/checkin` | Check-in d'un agent |

### `flask_file` (File Store)

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/files` | Lister les payloads disponibles |
| `POST` | `/files/upload` | Uploader un beacon |
| `GET` | `/files/<name>` | Télécharger un beacon |

---

## ⚠️ Avertissement légal

> Ce projet est **strictement éducatif**.  
> Son utilisation est **uniquement autorisée** dans un environnement isolé sur lequel vous avez une autorisation explicite.  
> Toute utilisation sur des systèmes tiers sans autorisation est **illégale** et contraire à l'éthique.  
> L'auteur décline toute responsabilité pour un usage malveillant.

---

## 📜 Licence

[Apache 2.0](./LICENSE) — © Tokzeen
