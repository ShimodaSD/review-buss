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
