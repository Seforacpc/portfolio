import requests
import pandas as pd
from collections import Counter
import re

API_URL = "http://127.0.0.1:5002/get_articles"

response = requests.get(API_URL)
articles = response.json()

df = pd.DataFrame(articles)

# nettoyer texte
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text

words = []

for title in df["title"]:
    text = clean_text(title)
    words.extend(text.split())

# mots inutiles
stopwords = {
    "le","la","les","de","du","des","un","une","et","en","à",
    "pour","sur","dans","avec","par","ce","cette"
}

filtered_words = [w for w in words if w not in stopwords and len(w) > 3]

word_counts = Counter(filtered_words)

top_words = word_counts.most_common(15)

df_keywords = pd.DataFrame(top_words, columns=["keyword","count"])

df_keywords.to_excel("data/news_keywords.xlsx", index=False)

print("Analyse terminée : news_keywords.xlsx")