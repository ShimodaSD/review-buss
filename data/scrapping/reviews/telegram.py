"""Envio de notificações pendentes ao Telegram."""
import json
import os
import urllib.parse
import urllib.request


def notify(conn):
    while True:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute('''SELECT g.name, g.reviewer_name, g.star_rating, g.comment
                    FROM telegram_review_notifications n JOIN google_reviews g ON g.name = n.review_name
                    WHERE n.sent_at IS NULL ORDER BY g.created_at, g.name
                    FOR UPDATE OF n SKIP LOCKED LIMIT 1''')
                review = cur.fetchone()
                if review is None:
                    return
                name, reviewer, rating, comment = review
                text = f"Nova avaliação no Google\n{reviewer or 'Anônimo'} — {rating or 'Sem nota'}\n{comment or 'Sem comentário'}"[:4096]
                data = urllib.parse.urlencode({'chat_id': os.environ['TELEGRAM_CHAT_ID'], 'text': text}).encode()
                request = urllib.request.Request('https://api.telegram.org/bot' + os.environ['TELEGRAM_BOT_TOKEN'] + '/sendMessage', data=data)
                with urllib.request.urlopen(request, timeout=30) as response:
                    if not json.load(response).get('ok'):
                        raise RuntimeError('Telegram não confirmou o envio')
                cur.execute('UPDATE telegram_review_notifications SET sent_at = now() WHERE review_name = %s', (name,))


