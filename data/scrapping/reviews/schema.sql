CREATE TABLE IF NOT EXISTS google_reviews (
    name text PRIMARY KEY,
    review_id text,
    reviewer_name text,
    reviewer_photo_url text,
    reviewer_is_anonymous boolean,
    star_rating text,
    comment text,
    created_at timestamptz,
    updated_at timestamptz,
    reply_comment text,
    reply_updated_at timestamptz,
    reply_state text,
    reply_policy_violation text,
    reply_url text,
    synced_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS google_review_media (
    review_name text NOT NULL REFERENCES google_reviews(name) ON DELETE CASCADE,
    position integer NOT NULL CHECK (position >= 0),
    thumbnail_url text,
    thumbnail_label text,
    video_url text,
    PRIMARY KEY (review_name, position)
);

CREATE TABLE IF NOT EXISTS reviews (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source text NOT NULL,
    source_id text NOT NULL,
    comment text,
    created_at timestamptz,
    source_url text,
    UNIQUE (source, source_id)
);

-- Include Google reviews imported before the unified table existed.
INSERT INTO reviews (source, source_id, comment, created_at)
SELECT 'google', name, comment, created_at FROM google_reviews
ON CONFLICT (source, source_id) DO UPDATE SET
    comment = EXCLUDED.comment, created_at = EXCLUDED.created_at;


CREATE TABLE IF NOT EXISTS google_review_sync (
    location text PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS telegram_review_notifications (
    review_name text PRIMARY KEY REFERENCES google_reviews(name) ON DELETE CASCADE,
    sent_at timestamptz
);
