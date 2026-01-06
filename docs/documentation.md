# Data eng practice

## Synthetic data generation
Ne pas hésiter à faire des données de test solides qui essaye de représenter des cas réels.
Maintenant avec l'IA on peut faire générer des scripts python pour faire ça aisément.

# Modelisation 
1. partir du métier
2. faire une modélisation logique métier
3. faire une modélisation physique technique

## Star schema
1. On regarde les donnée à la main :
    - On identifie ce qui est en commun
    - les dim
    - les fact (quelle granulatité ??)
2. ajouter des colonnes 'source' dans les dim et fact quand on fait de l'unification

## Data vault
hub . sat . link