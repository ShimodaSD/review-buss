"""Import every page of reviews for one Google Business Profile location."""
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request

import psycopg


def pages(parent, token):
    url = f'https://mybusiness.googleapis.com/v4/{parent}/reviews'
    page_token = None
    while True:
        query = {'pageSize': 50}
        if page_token:
            query['pageToken'] = page_token
        request = urllib.request.Request(url + '?' + urllib.parse.urlencode(query), headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(request, timeout=30) as response:
            page = json.load(response)
        yield page.get('reviews', [])
        page_token = page.get('nextPageToken')
        if not page_token:
            break


def main():
    parent = os.environ['GOOGLE_LOCATION']
    if not __import__('re').fullmatch(r'accounts/[0-9]+/locations/[0-9]+', parent):
        raise ValueError('GOOGLE_LOCATION must be accounts/<id>/locations/<id>')
    with psycopg.connect(os.environ['DATABASE_URL']) as conn:
        with conn.cursor() as cur:
            cur.execute(Path(__file__).with_name('schema.sql').read_text())
            count = 0
            for reviews in pages(parent, os.environ['GOOGLE_ACCESS_TOKEN']):
                for review in reviews:
                    reviewer = review.get('reviewer') or {}
                    reply = review.get('reviewReply') or {}
                    cur.execute('''INSERT INTO google_reviews
                        (name, review_id, reviewer_name, reviewer_photo_url, reviewer_is_anonymous, star_rating, comment, created_at, updated_at, reply_comment, reply_updated_at, reply_state, reply_policy_violation, reply_url)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (name) DO UPDATE SET
                        (review_id, reviewer_name, reviewer_photo_url, reviewer_is_anonymous, star_rating, comment, created_at, updated_at, reply_comment, reply_updated_at, reply_state, reply_policy_violation, reply_url, synced_at) =
                        (EXCLUDED.review_id, EXCLUDED.reviewer_name, EXCLUDED.reviewer_photo_url, EXCLUDED.reviewer_is_anonymous, EXCLUDED.star_rating, EXCLUDED.comment, EXCLUDED.created_at, EXCLUDED.updated_at, EXCLUDED.reply_comment, EXCLUDED.reply_updated_at, EXCLUDED.reply_state, EXCLUDED.reply_policy_violation, EXCLUDED.reply_url, now())''',
                        (review['name'], review.get('reviewId'), reviewer.get('displayName'), reviewer.get('profilePhotoUrl'), reviewer.get('isAnonymous'), review.get('starRating'), review.get('comment'), review.get('createTime'), review.get('updateTime'), reply.get('comment'), reply.get('updateTime'), reply.get('reviewReplyState'), reply.get('policyViolation'), review.get('reviewReplyUrl')))
                    cur.execute('DELETE FROM google_review_media WHERE review_name = %s', (review['name'],))
                    for position, media in enumerate(review.get('reviewMediaItems') or []):
                        cur.execute('INSERT INTO google_review_media VALUES (%s, %s, %s, %s, %s)', (review['name'], position, media.get('thumbnailUrl'), media.get('thumbnailLabel'), media.get('videoUrl')))
                    count += 1
    print(f'Imported {count} reviews')


if __name__ == '__main__':
    main()
