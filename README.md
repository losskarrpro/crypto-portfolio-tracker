# Crypto Portfolio Tracker

## Overview

**crypto-portfolio-tracker** est un outil CLI Python complet pour suivre votre portefeuille de cryptomonnaies en 2026. Il lit un fichier `config.json` contenant vos coins et quantités, récupère les prix live gratuits via l'API CoinGecko, calcule la valeur totale, le PnL (Profit and Loss), l'évolution en %, affiche un tableau ASCII coloré (vert pour gains, rouge pour pertes) avec [rich](https://rich.readthedocs.io/), permet l'export CSV et les stats journalières.

## Installation

1. Clonez le repo ou téléchargez les fichiers du projet.
2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Créez ou éditez `config.json` avec votre portefeuille (exemple) :

```json
{
  "portfolio": {
    "BTC": 1.0,
    "ETH": 5.0,
    "SOL": 100.0
  }
}
```

- `coins` : Clés = symboles CoinGecko (majuscules), Valeurs = quantités détenues.

## Usage CLI

Utilisez `argparse` pour les commandes. Exécutez depuis le dossier racine.

```bash
python main.py --help
```

### Commandes principales

- **Afficher le tableau du portefeuille** (prix live, valeur, PnL, % évolution, couleurs vert/rouge) :
  ```bash
  python main.py display
  ```

- **Exporter en CSV** (inclut prix, quantités, valeurs, PnL) :
  ```bash
  python main.py export --output portfolio.csv
  ```

- **Stats journalières** (évolution sur 24h, moyennes, totaux) :
  ```bash
  python main.py stats
  ```

### Exemple de sortie `display`

```
┌────────────┬────────────┬────────────┬────────────┬────────────┬────────────┐
│ Coin       │ Quantité   │ Prix ($)   │ Valeur ($) │ PnL ($)    │ Évolution % │
├────────────┼────────────┼────────────┼────────────┼────────────┼────────────┤
│ BTC        │ 1.000      │ 95,000.00  │ 95,000.00  │ +5,000.00  │ +5.56%     │
│ ETH        │ 5.000      │ 4,200.00   │ 21,000.00  │ -1,000.00  │ -4.55%     │
│ SOL        │ 100.000    │ 180.00     │ 18,000.00  │ +2,000.00  │ +12.50%    │
├────────────┼────────────┼────────────┼────────────┼────────────┼────────────┤
│ TOTAL      │            │            │ 134,000.00 │ +6,000.00  │ +4.69%     │
└────────────┴────────────┴────────────┴────────────┴────────────┴────────────┘
```

Valeur totale : **134,000.00 $** | PnL global : **+6,000.00 $ (+4.69%)**

## Tests

Exécutez les unit tests :
```bash
python test_portfolio.py
```

## Fichiers du projet

- `main.py` : Point d'entrée CLI avec `argparse` et `rich`.
- `portfolio.py` : Logique core (fetch CoinGecko, calculs, tableau).
- `config.json` : Exemple de configuration.
- `requirements.txt` : `requests`, `rich`.
- `test_portfolio.py` : Tests unitaires.
- `.gitignore` : Fichiers ignorés (venv, __pycache__, etc.).

## Limitations

- API CoinGecko gratuite (limite ~50 calls/min).
- Pas de persistance historique (stats journalières basées sur API 24h).
- Supporte tous les coins listés sur CoinGecko.

## Created & Signed by Lumena - IA autonome de Charles 2026