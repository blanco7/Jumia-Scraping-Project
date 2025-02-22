# Projet Final : Jumia.sn Scraping
# by ANANOU Kokou Germain
"""""
Dans le cadre de ce projet, nous utiliserons le web scraping pour extraire des informations détaillées données des produits (comme les noms, prix, avis, et autres détails) 
du site de Jumia Senegal et les stocker dans un fichier CSV.

Avant de passer a l'etape de scraping du site, j'ai parcouru les conditions d'utilisation du site et eplucher le fichier https://www.jumia.sn/robots.txt. 
Les conditions suivantes sont precisees:

    Site en public
    Le bot doit respecter les règles suivantes
    L'exploration de sites est autorisée si l'agent utilisateur identifie clairement qu'il s'agit d'un robot et si le propriétaire du robot utilise moins de 200 requêtes par minute.
    le propriétaire du bot et utilise moins de 200 requêtes par minute
    L'identification du bot doit comporter l'url du propriétaire ou un contact si nous avons besoin de le contacter.
    Les robots dont l'agent utilisateur est falsifié seront bloqués.
    Les robots qui tentent d'utiliser trop d'adresses IP pour augmenter leurs performances peuvent également être bloqués.
    Si vous avez besoin de plus de 200 RPM, veuillez contacter l'email techops at jumia com.

Jumia autorise l'exploration du site tant que vous respectez certaines conditions

"""""
# Exercice 1 : Configuration du scraping
# Étape 1 : Charger une page de Jumia

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# URL de la page Jumia à scraper (par exemple, smartphones)
url = "https://www.jumia.sn/smartphones/"

"""""
Les conditions d'utilisations de Jumia exige que L'identification du bot doit comporter l'URL du propriétaire ou un contact si nous avons besoin de le contacter.
Pour contourner cela. Nous allons utiliser un User-Agent correspond à celui d'un navigateur classique (Google Chrome sous Windows 10). 
Il permet de se faire passer pour un utilisateur humain plutôt qu’un bot.

"""""
# Configuration du User-Agent conforme à robots.txt de Jumia
headers = {
    'User-Agent': 'JumiaScraperBot/1.0 (+https://github.com/blanco7/Jumia-Scraping-Project)',
    'From': 'kokou.germain.etu@esmt.sn' 
}

# Exercice 2 : Extraire les données des produits
response = requests.get(url)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    print("Page téléchargée avec succès !")
else:
    print(f"Erreur lors du téléchargement : {response.status_code}")

# Extraction des données des produits
# Trouver les conteneurs de produits
products = soup.find_all("article", class_="prd _fb col c-prd")

# Nettoyage du prix 
def clean_price(raw_price):
    """Convertit le prix texte (ex: '1 000 FCFA') en nombre décimal."""
    if not raw_price:
        return 0.0
    
    # Supprime 'FCFA', les espaces, et convertit en float
    cleaned = raw_price.replace('FCFA', '').replace(' ', '').strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0  # Si conversion impossible
    
# Parcourir chaque produit pour extraire les informations
for product in products[:5]:
    name = product.find("h3", class_="name").text.strip()
    raw_price = product.find("div", class_="prc").text.strip()
    price = clean_price(raw_price)  # ← Nettoyage ici aussi
    rating = product.find("div", class_="stars")
    
    rating_text = rating.text.strip() if rating else "Pas d'avis"
    
    print(f"Nom : {name}")
    print(f"Prix : {price} FCFA")  # Affiche le prix nettoyé
    print(f"Avis : {rating_text}")
    print("-" * 30)

# Exercice 3 : Stocker les données dans un fichier CSV

# Liste pour stocker les données
data = []

# Extraire les données et les stocker dans une liste
for product in products:
    name = product.find("h3", class_="name").text.strip()
    price = product.find("div", class_="prc").text.strip()
    rating = product.find("div", class_="stars")
    rating_text = rating.text.strip() if rating else "Pas d'avis"
    
    data.append({"Nom": name, "Prix": price, "Avis": rating_text})

# Créer un DataFrame
df = pd.DataFrame(data)

# Sauvegarder dans un fichier CSV du test
df.to_csv("jumia_products.csv", index=False, encoding="utf-8")
print("Les données ont été sauvegardées dans 'jumia_products.csv'")

    
# Exercice 4 : Nettoyage et optimisation
def get_products(url):
    """Télécharge la page et retourne la liste des produits."""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur lors de la requête : {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    products = soup.find_all("article", class_="prd _fb col c-prd")
    return products

   
def extract_product_data(products):
    """Extrait les informations des produits et les retourne sous forme de liste."""
    data = []
    for product in products:
        name_tag = product.find("h3", class_="name")
        price_tag = product.find("div", class_="prc")
        rating_tag = product.find("div", class_="stars")

        # Nettoyage des données
        name = name_tag.text.strip() if name_tag else "Nom inconnu"
        raw_price = price_tag.text.strip() if price_tag else ""
        price = clean_price(raw_price)  # ← Utilisation de la fonction de nettoyage
        rating = rating_tag.text.strip() if rating_tag else "Pas d'avis"

        data.append({"Nom": name, "Prix": price, "Avis": rating})
    return data


def save_to_csv(data, filename):
    """Sauvegarde les données dans un fichier CSV."""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"Les données ont été sauvegardées dans '{filename}'")


# Exemple d'exécution
url = "https://www.jumia.sn/smartphones/"
products = get_products(url)
data = extract_product_data(products)
save_to_csv(data, "jumia_products.csv")

# Exercice 5 : Ajouter la pagination

def scrape_multiple_pages(base_url, num_pages):
    """Scrape plusieurs pages Jumia et retourne les données."""
    all_data = []
    for page in range(1, num_pages + 1):
        print(f"Scraping page {page}...")
        url = f"{base_url}?page={page}"
        products = get_products(url)
        data = extract_product_data(products)
        all_data.extend(data)

        time.sleep(2)  # Pause entre chaque page pour éviter d'être bloqué
    return all_data

# Exécution
base_url = "https://www.jumia.sn/smartphones/"
all_data = scrape_multiple_pages(base_url, 3)  # Scrape les 3 premières pages
save_to_csv(all_data, "jumia_all_products.csv")