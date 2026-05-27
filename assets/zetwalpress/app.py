from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Sefora972!",
    "database": "sauvegarde_data",
    "port": 3306
}


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Bienvenue sur l'API de sauvegarde d'articles ! 🚀"}), 200


@app.route("/get_articles", methods=["GET"])
def get_articles():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, title, link, source, urlToImage, created_at
            FROM articles
            ORDER BY id DESC
        """)
        articles = cursor.fetchall()
        return jsonify(articles), 200

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération : {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/save_article", methods=["POST"])
def save_article():
    conn = None
    cursor = None
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Aucune donnée JSON reçue"}), 400

        required_fields = ["title", "link", "source", "urlToImage"]
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                return jsonify({"error": f"Champ manquant ou vide : {field}"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Vérifier si l'article existe déjà via son lien
        cursor.execute("SELECT id FROM articles WHERE link = %s", (data["link"],))
        existing = cursor.fetchone()

        if existing:
            return jsonify({"message": "⚠️ Article déjà enregistré"}), 200

        sql = """
            INSERT INTO articles (title, link, source, urlToImage)
            VALUES (%s, %s, %s, %s)
        """
        values = (
            data["title"],
            data["link"],
            data["source"],
            data["urlToImage"]
        )

        cursor.execute(sql, values)
        conn.commit()

        return jsonify({"message": "✅ Article ajouté"}), 201

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la sauvegarde : {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/delete_article/<int:id>", methods=["DELETE"])
def delete_article(id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM articles WHERE id = %s", (id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "⚠️ Aucun article trouvé avec cet id"}), 404

        return jsonify({"message": "✅ Article supprimé !"}), 200

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la suppression : {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/stats", methods=["GET"])
def get_stats():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Total d'articles
        cursor.execute("SELECT COUNT(*) AS total_articles FROM articles")
        total_articles = cursor.fetchone()["total_articles"]

        # Articles par source
        cursor.execute("""
            SELECT source, COUNT(*) AS count
            FROM articles
            GROUP BY source
            ORDER BY count DESC
        """)
        articles_by_source = cursor.fetchall()

        # Articles par jour
        cursor.execute("""
            SELECT DATE(created_at) AS day, COUNT(*) AS count
            FROM articles
            GROUP BY DATE(created_at)
            ORDER BY day DESC
        """)
        articles_by_day = cursor.fetchall()

        return jsonify({
            "total_articles": total_articles,
            "articles_by_source": articles_by_source,
            "articles_by_day": articles_by_day
        }), 200

    except Exception as e:
        return jsonify({"error": f"Erreur stats : {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    print("🚀 Flask API démarrée sur le port 5002")
    app.run(debug=True, host="0.0.0.0", port=5002)