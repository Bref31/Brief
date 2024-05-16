import sqlite3

# Connexion à la base de données SQLite
conn = sqlite3.connect('/data/sales.db')
cursor = conn.cursor()

# Création des tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS produits (
    id INTEGER PRIMARY KEY,
    nom TEXT,
    categorie TEXT,
    prix REAL
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS magasins (
    id INTEGER PRIMARY KEY,
    nom TEXT,
    ville TEXT,
    region TEXT
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS ventes (
    id INTEGER PRIMARY KEY,
    date TEXT,
    montant REAL,
    produit_id INTEGER,
    magasin_id INTEGER,
    FOREIGN KEY (produit_id) REFERENCES produits(id),
    FOREIGN KEY (magasin_id) REFERENCES magasins(id)
)
''')

# Création de la table pour stocker les résultats des analyses
cursor.execute('''
CREATE TABLE IF NOT EXISTS analyse_ventes (
    id INTEGER PRIMARY KEY,
    vente_id INTEGER,
    produit_id INTEGER,
    ventes_totales REAL,
    chiffre_affaires_total REAL,
    ventes_par_region TEXT,
    FOREIGN KEY (vente_id) REFERENCES ventes(id),
    FOREIGN KEY (produit_id) REFERENCES produits(id)
)
''')

# Commit des changements et fermeture de la connexion
conn.commit()
conn.close()

print("Base de données et tables créées avec succès.")
