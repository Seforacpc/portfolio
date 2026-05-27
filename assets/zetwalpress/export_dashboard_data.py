import requests
import pandas as pd

API_ARTICLES = "http://127.0.0.1:5002/get_articles"
API_STATS = "http://127.0.0.1:5002/stats"

def detect_category(link):
    link = str(link).lower()

    if "/politique/" in link or "/elections/" in link:
        return "Politique"
    elif "/sports/" in link:
        return "Sports"
    elif "/culture/" in link:
        return "Culture"
    elif "/economie/" in link:
        return "Economie"
    elif "/justice/" in link:
        return "Justice"
    elif "/education/" in link:
        return "Education"
    elif "/societe/" in link or "/social/" in link:
        return "Societe"
    elif "/environnement/" in link:
        return "Environnement"
    else:
        return "Autre"


# récupérer données API
articles = requests.get(API_ARTICLES).json()
stats = requests.get(API_STATS).json()

# dataframe articles
df_articles = pd.DataFrame(articles)

if not df_articles.empty:
    df_articles["category"] = df_articles["link"].apply(detect_category)
    df_articles["created_at"] = pd.to_datetime(df_articles["created_at"], errors="coerce")
    df_articles["date_only"] = df_articles["created_at"].dt.date

# stats API
df_sources = pd.DataFrame(stats["articles_by_source"])
df_days = pd.DataFrame(stats["articles_by_day"])

# stats catégorie
if not df_articles.empty:
    df_category = (
        df_articles.groupby("category")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
else:
    df_category = pd.DataFrame(columns=["category", "count"])

# export excel
with pd.ExcelWriter("data/zetwalpress_news.xlsx", engine="openpyxl") as writer:

    df_articles.to_excel(writer, sheet_name="articles", index=False)

    df_sources.to_excel(writer, sheet_name="articles_by_source", index=False)

    df_days.to_excel(writer, sheet_name="articles_by_day", index=False)

    df_category.to_excel(writer, sheet_name="articles_by_category", index=False)


print("Fichier généré : data/zetwalpress_news.xlsx")