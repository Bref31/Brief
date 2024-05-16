import sqlite3
import csv
import requests

# URLs des fichiers CSV partagées par le client
urls = {
    "ventes": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSawI56WBC64foMT9pKCiY594fBZk9Lyj8_bxfgmq-8ck_jw1Z49qDeMatCWqBxehEVoM6U1zdYx73V/pub?gid=0&single=true&output=csv",
    "produits": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSawI56WBC64foMT9pKCiY594fBZk9Lyj8_bxfgmq-8ck_jw1Z49qDeMatCWqBxehEVoM6U1zdYx73V/pub?gid=714623615&single=true&output=csv",
    "magasins": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSawI56WBC64foMT9pKCiY594fBZk9Lyj8_bxfgmq-8ck_jw1Z49qDeMatCWqBxehEVoM6U1zdYx73V/pub?gid=760830694&single=true&output=csv"
}

# Connexion à la base de données SQLite
conn = sqlite3.connect('/data/sales.db')
cursor = conn.cursor()

# Création des tables
cursor.execute("CREATE TABLE IF NOT EXISTS produits (id INTEGER PRIMARY KEY, nom TEXT, categorie TEXT, prix REAL);")
cursor.execute("CREATE TABLE IF NOT EXISTS magasins (id INTEGER PRIMARY KEY, nom TEXT, ville TEXT, region TEXT);")
cursor.execute("CREATE TABLE IF NOT EXISTS ventes (id INTEGER PRIMARY KEY, date TEXT, montant REAL, produit_id INTEGER, magasin_id INTEGER, FOREIGN KEY (produit_id) REFERENCES produits(id), FOREIGN KEY (magasin_id) REFERENCES magasins(id));")

# Fonctions pour importer les données
def convert_value(value, data_type):
    if value is None or value == '':
        return None
    if data_type == "INTEGER":
        return int(value) if value.isdigit() else None
    elif data_type == "REAL":
        try:
            return float(value)
        except ValueError:
            return None
    elif data_type == "TEXT":
        return str(value)
    else:
        return value

def import_data(url, table_name, columns, data_types):
    response = requests.get(url)
    if response.status_code == 200:
        data = csv.reader(response.text.splitlines())
        headers = next(data)  # Ignorer les en-têtes
        for row in data:
            if len(row) < len(columns.split(',')):
                row += [None] * (len(columns.split(',')) - len(row))
            validated_row = [convert_value(value, data_type) for value, data_type in zip(row, data_types)]
            placeholders = ', '.join('?' * len(validated_row))
            query = f'INSERT OR IGNORE INTO {table_name} ({columns}) VALUES ({placeholders})'
            cursor.execute(query, validated_row)
        conn.commit()
    else:
        print(f"Erreur lors du téléchargement des données depuis {url}. HTTP Status Code: {response.status_code}")

# Importer les données
import_data(urls["produits"], "produits", "id, nom, categorie, prix", ["INTEGER", "TEXT", "TEXT", "REAL"])
import_data(urls["magasins"], "magasins", "id, nom, ville, region", ["INTEGER", "TEXT", "TEXT", "TEXT"])
import_data(urls["ventes"], "ventes", "id, date, montant, produit_id, magasin_id", ["INTEGER", "TEXT", "REAL", "INTEGER", "INTEGER"])

# Requêtes pour les calculs
cursor.execute('''
INSERT INTO chiffre_affaires_total (date, total_ventes)
SELECT CURRENT_DATE, COALESCE(SUM(v.montant * p.prix), 0)
FROM ventes v
JOIN produits p ON v.produit_id = p.id
ON CONFLICT(date) DO UPDATE SET total_ventes = EXCLUDED.total_ventes;
''')

cursor.execute('''
INSERT INTO ventes_par_produit (produit_id, total_ventes)
SELECT produit_id, COALESCE(SUM(v.montant * p.prix), 0)
FROM ventes v
JOIN produits p ON v.produit_id = p.id
GROUP BY produit_id
ON CONFLICT(produit_id) DO UPDATE SET total_ventes = EXCLUDED.total_ventes;
''')

cursor.execute('''
INSERT INTO ventes_par_region (region, total_ventes)
SELECT m.region, COALESCE(SUM(v.montant * p.prix), 0)
FROM ventes v
JOIN magasins m ON v.magasin_id = m.id
JOIN produits p ON v.produit_id = p.id
GROUP BY m.region
ON CONFLICT(region) DO UPDATE SET total_ventes = EXCLUDED.total_ventes;
''')

# Affichage des résultats
cursor.execute('SELECT total_ventes FROM chiffre_affaires_total WHERE date = CURRENT_DATE;')
result_1 = cursor.fetchone()
print("Chiffre d'affaires total:", result_1[0])

cursor.execute('SELECT * FROM ventes_par_produit;')
result_2 = cursor.fetchall()
print("Ventes par produit:", result_2)

cursor.execute('SELECT region, total_ventes FROM ventes_par_region;')
result_3 = cursor.fetchall()
print("Ventes par région:", result_3)

conn.commit()
conn.close()
