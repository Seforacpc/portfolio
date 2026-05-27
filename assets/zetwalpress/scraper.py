from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os
import time
import csv

app = Flask(__name__)

SOURCES = [
    "https://www.martinique.franceantilles.fr/",
]

cached_articles = []
last_fetch_time = 0
CACHE_DURATION = 10 * 60  # 10 minutes

API_SAVE_URL = "http://127.0.0.1:5002/save_article"

def save_to_csv(articles, filename="articles.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "link", "source", "urlToImage"])
        writer.writeheader()
        writer.writerows(articles)

def send_article_to_api(article):
    try:
        response = requests.post(API_SAVE_URL, json=article, timeout=10)
        if response.status_code in (200, 201):
            print(f"✅ Enregistré dans MySQL : {article['title']}")
        else:
            print(f"⚠️ Erreur API {response.status_code} : {response.text}")
    except Exception as e:
        print(f"❌ Impossible d'envoyer l'article à l'API : {e}")

def scrape_articles(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = []
        for article in soup.select("article h2 a"):
            title = article.text.strip()
            link = article.get("href", "")
            if link and not link.startswith("http"):
                link = url.rstrip("/") + "/" + link.lstrip("/")

            parent = article.find_parent()
            img = parent.find("img") if parent else None
            image_url = img.get("src", "https://via.placeholder.com/150") if img else "https://via.placeholder.com/150"

            article_data = {
                "title": title,
                "link": link,
                "source": "France-Antilles",
                "urlToImage": image_url
            }

            articles.append(article_data)

        return articles
    except Exception as e:
        print(f"❌ Erreur scraping {url} : {e}")
        return []

@app.route("/")
def home():
    return "<h1>✅ API de Scraping Active</h1><p>Utilisez <b>/scrape</b> pour récupérer les articles.</p>"

@app.route("/scrape", methods=["GET"])
def scrape_all():
    global cached_articles, last_fetch_time
    now = time.time()

    if not cached_articles or now - last_fetch_time > CACHE_DURATION:
        print("🔁 Scraping en cours...")
        all_articles = []
        for source in SOURCES:
            scraped = scrape_articles(source)
            all_articles.extend(scraped)

            for article in scraped:
                send_article_to_api(article)

        cached_articles = all_articles
        last_fetch_time = now
        save_to_csv(cached_articles)
    else:
        print("⚡ Articles servis depuis le cache")

    return jsonify(cached_articles)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)