"""Persistência das avaliações e da fila de notificações."""
from pathlib import Path

from google import pages


def sync(conn, parent, token):
    with conn.cursor() as cur:
        cur.execute(Path(__file__).with_name('schema.sql').read_text())
        cur.execute('SELECT pg_advisory_xact_lock(hashtext(%s))', (parent,))
        cur.execute('SELECT 1 FROM google_review_sync WHERE location = %s', (parent,))
        baseline = cur.fetchone() is None
        count = 0
        for reviews in pages(parent, token):
            for review in reviews:
                cur.execute('SELECT 1 FROM google_reviews WHERE name = %s', (review['name'],))
                is_new = cur.fetchone() is None
                reviewer = review.get('reviewer') or {}
                reply = review.get('reviewReply') or {}
                cur.execute('''INSERT INTO google_reviews
                    (name, review_id, reviewer_name, reviewer_photo_url, reviewer_is_anonymous, star_rating, comment, created_at, updated_at, reply_comment, reply_updated_at, reply_state, reply_policy_violation, reply_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE SET
                    (review_id, reviewer_name, reviewer_photo_url, reviewer_is_anonymous, star_rating, comment, created_at, updated_at, reply_comment, reply_updated_at, reply_state, reply_policy_violation, reply_url, synced_at) =
                    (EXCLUDED.review_id, EXCLUDED.reviewer_name, EXCLUDED.reviewer_photo_url, EXCLUDED.reviewer_is_anonymous, EXCLUDED.star_rating, EXCLUDED.comment, EXCLUDED.created_at, EXCLUDED.updated_at, EXCLUDED.reply_comment, EXCLUDED.reply_updated_at, EXCLUDED.reply_state, EXCLUDED.reply_policy_violation, EXCLUDED.reply_url, now())''',
                    (review['name'], review.get('reviewId'), reviewer.get('displayName'), reviewer.get('profilePhotoUrl'), reviewer.get('isAnonymous'), review.get('starRating'), review.get('comment'), review.get('createTime'), review.get('updateTime'), reply.get('comment'), reply.get('updateTime'), reply.get('reviewReplyState'), reply.get('policyViolation'), review.get('reviewReplyUrl')))
                cur.execute('''INSERT INTO reviews (source, source_id, comment, created_at)
                    VALUES ('google', %s, %s, %s)
                    ON CONFLICT (source, source_id) DO UPDATE SET
                    comment = EXCLUDED.comment, created_at = EXCLUDED.created_at''',
                    (review['name'], review.get('comment'), review.get('createTime')))
                cur.execute('DELETE FROM google_review_media WHERE review_name = %s', (review['name'],))
                for position, media in enumerate(review.get('reviewMediaItems') or []):
                    cur.execute('INSERT INTO google_review_media VALUES (%s, %s, %s, %s, %s)', (review['name'], position, media.get('thumbnailUrl'), media.get('thumbnailLabel'), media.get('videoUrl')))
                if is_new and not baseline:
                    cur.execute('INSERT INTO telegram_review_notifications (review_name) VALUES (%s) ON CONFLICT DO NOTHING', (review['name'],))
                count += 1
        cur.execute('INSERT INTO google_review_sync (location) VALUES (%s) ON CONFLICT DO NOTHING', (parent,))
    return count
