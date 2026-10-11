"""Read-only NewsPulse API backed by the ETL's PostgreSQL news_data table."""

from __future__ import annotations

import json
import logging
import os
from contextlib import closing
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

APP_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = APP_DIR.parent
ENV_FILE = Path(os.environ.get("NEWSPULSE_ENV_FILE", REPO_DIR / "config" / ".env"))
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def load_local_env():
    """Load simple KEY=VALUE entries without overriding process variables."""
    try:
        lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key in {"database", "user", "password"}:
            os.environ.setdefault(key, value)


load_local_env()


def connect_database():
    import psycopg2

    return psycopg2.connect(
        host=os.environ.get("NEWSPULSE_DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("NEWSPULSE_DB_PORT", "5433")),
        dbname=os.environ.get("NEWSPULSE_DB_NAME", os.environ.get("database", "airflow")),
        user=os.environ.get("NEWSPULSE_DB_USER", os.environ.get("user", "airflow")),
        password=os.environ.get("NEWSPULSE_DB_PASSWORD", os.environ.get("password", "airflow")),
        connect_timeout=5,
        application_name="newspulse_read_only",
    )


def fetch_news():
    """Return the newest stored row per ID in a read-only transaction."""
    query = """
        SELECT DISTINCT ON (news_id)
            news_id, news_title, news_description, news_url,
            news_published_at, lang, source_id, source_name, source_url,
            source_country, image, content
        FROM public.news_data
        ORDER BY news_id, news_published_at DESC NULLS LAST,
                 (image IS NOT NULL) DESC, (content IS NOT NULL) DESC
    """
    with closing(connect_database()) as connection:
        connection.set_session(readonly=True)
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

    articles = []
    for row in rows:
        (news_id, title, description, url, published_at, lang, source_id,
         source_name, source_url, source_country, image, content) = row
        articles.append({
            "id": news_id,
            "title": title,
            "description": description,
            "url": url,
            "publishedAt": published_at.isoformat() if published_at else None,
            "lang": lang,
            "image": image,
            "content": content,
            "source": {
                "id": source_id,
                "name": source_name,
                "url": source_url,
                "country": source_country,
            },
        })
    articles.sort(key=lambda article: article["publishedAt"] or "", reverse=True)
    return articles


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(APP_DIR / "frontend"), **kwargs)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/news":
            self.send_news()
            return
        if path == "/api/health":
            self.send_health()
            return
        super().do_GET()

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_news(self):
        try:
            articles = fetch_news()
            self.send_json({
                "articles": articles,
                "totalArticles": len(articles),
                "dataSource": "PostgreSQL",
            })
        except Exception:
            logging.exception("Falha ao consultar PostgreSQL para o NewsPulse")
            self.send_json({
                "error": "Não foi possível consultar o PostgreSQL. Verifique se o serviço está ativo, se a tabela news_data existe e se a conexão está configurada."
            }, 503)

    def send_health(self):
        try:
            with closing(connect_database()) as connection:
                connection.set_session(readonly=True)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            self.send_json({"status": "ok", "database": "connected"})
        except Exception:
            self.send_json({"status": "error", "database": "unavailable"}, 503)


if __name__ == "__main__":
    port = int(os.environ.get("NEWSPULSE_PORT", "4173"))
    db_port = os.environ.get("NEWSPULSE_DB_PORT", "5433")
    print(f"NewsPulse disponível em http://localhost:{port} (PostgreSQL: 127.0.0.1:{db_port})")
    bind = os.environ.get("NEWSPULSE_BIND", "127.0.0.1")
    ThreadingHTTPServer((bind, port), Handler).serve_forever()
