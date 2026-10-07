# Sales Dashboard : Analyse des ventes avec Streamlit

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Visualisation-3F4F75?logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data-150458?logo=pandas&logoColor=white)

Tableau de bord interactif pour explorer les performances commerciales d'un supermarché, repérer les tendances et appuyer la prise de décision par les données.


![Aperçu du dashboard](assets/dashboard_preview.png)

---

## Contexte et objectifs

Ce projet a été réalisé dans le cadre d'un cours de **visualisation de données**. Il répond à cinq questions métier :

- Quelles villes et quelles gammes de produits génèrent le plus de chiffre d'affaires ?
- Comment les ventes évoluent-elles dans le temps ?
- Quel est le profil des clients (genre, type de client, mode de paiement) ?
- Quel est le niveau de satisfaction client et comment varie-t-il ?
- Existe-t-il des relations entre prix, quantité, marge et note ?

---

## Fonctionnalités

### Filtres interactifs (barre latérale)
Ville · Gamme de produits · Mode de paiement · Genre · Note · Mois

Tous les indicateurs et graphiques se mettent à jour en temps réel selon les filtres.

### Indicateurs clés (KPI)

| KPI | Description |
|---|---|
| Ventes totales | Somme du chiffre d'affaires |
| Transactions | Nombre de ventes |
| Note moyenne | Satisfaction client (sur 10) |
| Panier moyen | Montant moyen par transaction |

### Visualisations

| Graphique | Objectif |
|---|---|
| Diagramme en barres | Comparer les ventes par gamme de produits ou par ville |
| Diagramme circulaire | Répartition des modes de paiement |
| Courbe temporelle | Évolution des ventes dans le temps |
| Histogramme | Distribution des montants de vente |
| Boxplot | Dispersion des ventes par catégorie, détection des valeurs atypiques |
| Scatter plot | Relation entre prix unitaire, quantité et montant |
| Heatmap | Corrélations entre variables numériques |
| Sunburst | Analyse hiérarchique (ville, gamme, paiement) |
| Gauge | Niveau global de satisfaction client |

---

## Données

Le dataset contient les transactions d'un supermarché sur plusieurs villes. Source : [Supermarket Sales, Kaggle](https://www.kaggle.com/datasets/aungpyaeap/supermarket-sales).

| Colonne | Description |
|---|---|
| `Invoice ID` | Identifiant de la facture |
| `Branch` / `City` | Succursale / ville |
| `Customer type` | Membre ou non-membre |
| `Gender` | Genre du client |
| `Product line` | Gamme de produits |
| `Unit price` / `Quantity` | Prix unitaire / quantité |
| `Tax 5%` / `Total` | Taxe / montant total |
| `Date` / `Time` | Date et heure de la vente |
| `Payment` | Mode de paiement |
| `Rating` | Note de satisfaction (1 à 10) |

---

## Installation et lancement

```bash
# 1. Cloner le dépôt
git clone https://github.com/<ton-utilisateur>/<ton-repo>.git
cd <ton-repo>

# 2. (Optionnel) Créer un environnement virtuel
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`.

---

## Structure du projet

```
├── app.py                  # Application Streamlit principale
├── data/
│   └── supermarket_sales.csv
├── assets/                 # Captures d'écran
├── requirements.txt
└── README.md
```

---

## Principaux enseignements

> À compléter avec tes propres résultats, par exemple :

- La gamme **X** représente **Y %** du chiffre d'affaires.
- Les ventes sont plus élevées en **[mois / jour / heure]**.
- La note moyenne est de **X/10**, avec peu de variation selon la ville.
- Les corrélations montrent que **[observation]**.

---

## Technologies

- **Python** : langage principal
- **Streamlit** : interface web interactive
- **Pandas** : nettoyage et manipulation des données
- **Plotly** : graphiques interactifs

---

## Pistes d'amélioration

- Export des données filtrées (CSV / Excel)
- Comparaison de périodes (mois vs mois précédent)
- Prévision des ventes (Prophet, ARIMA)
- Mode sombre / clair
- Déploiement sur Streamlit Community Cloud

---

## Auteur

**[Ton nom]** : [LinkedIn](https://linkedin.com/in/...) · [GitHub](https://github.com/...)
