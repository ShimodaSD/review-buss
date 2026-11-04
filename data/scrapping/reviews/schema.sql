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
