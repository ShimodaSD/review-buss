# Nipon Rotisserie review importer

Import reviews from a verified Google Business Profile into PostgreSQL. The importer follows every page and upserts the documented review and reviewer fields into columns. Re-running updates existing reviews; it does not delete reviews removed from Google.

1. Obtain Google Business Profile API access and an OAuth access token with the `https://www.googleapis.com/auth/business.manage` scope for a user who manages the location. Find the account and location IDs in the Business Profile APIs.
2. Install dependencies: `pip install .`
3. Fill in `.env` using `.env.example` as a guide. Load it into your shell with `set -a; source .env; set +a`.
4. Run `python data/scrapping/reviews/main.py`.

The database transaction commits only after all pages succeed. Access tokens expire; obtain a fresh token before running. Keep credentials out of source control. Google's API does not provide private reviewer contact details.

The importer initializes `data/scrapping/reviews/schema.sql` automatically. You can also initialize an existing database without importing reviews:

```sh
psql "$DATABASE_URL" -f data/scrapping/reviews/schema.sql
```

`google_reviews` stores review, reviewer and reply fields; `google_review_media` stores media items.

## Docker

Set `POSTGRES_PASSWORD`, `GOOGLE_LOCATION`, and `GOOGLE_ACCESS_TOKEN` in `.env`. Use a URL-safe password for the PostgreSQL connection string.

- `docker compose up --build` starts PostgreSQL and the React development server at http://localhost:5173.
- `docker compose --profile import run --build --rm importer` imports reviews. PostgreSQL data persists in a Docker volume.

The Python container uses Python 3.15. The backend is a placeholder and does not yet provide an API.


A tabela `reviews` reúne as avaliações importadas para uso futuro pelo frontend.


## Avisos diários no Telegram

1. Crie um bot com o [BotFather](https://core.telegram.org/bots/tutorial), inicie uma conversa com ele e obtenha o ID da conversa usando `getUpdates` da Bot API. Configure `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` no `.env`.
2. Configure `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` e `GOOGLE_REFRESH_TOKEN` de um usuário que gerencia o perfil, com o escopo `business.manage` e acesso offline. O importador renova o token automaticamente. Para execução manual, `GOOGLE_ACCESS_TOKEN` continua sendo aceito se não houver refresh token.
3. Execute `docker compose --profile daily up -d --build`. O serviço verifica imediatamente e depois a cada 24 horas, enquanto estiver ativo. Consulte os erros com `docker compose logs daily-importer`.

Na primeira execução bem-sucedida, as avaliações existentes são importadas sem aviso. Nas próximas, cada avaliação nova gera uma mensagem; avaliações editadas não geram aviso. A fila permanece no banco e falhas de envio são tentadas na próxima execução. Caso o processo seja interrompido depois de o Telegram aceitar uma mensagem e antes de registrar o envio, ela pode ser enviada novamente. A execução diária depende do Docker e do computador ou servidor permanecerem ligados.
