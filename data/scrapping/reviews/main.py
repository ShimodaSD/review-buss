"""Importa avaliações e envia notificações pendentes."""
import os
import re

import psycopg

from database import sync
from google import access_token
from telegram import notify


def main():
    parent = os.environ['GOOGLE_LOCATION']
    if not re.fullmatch(r'accounts/[0-9]+/locations/[0-9]+', parent):
        raise ValueError('GOOGLE_LOCATION must be accounts/<id>/locations/<id>')
    token = access_token()
    with psycopg.connect(os.environ['DATABASE_URL']) as conn:
        count = sync(conn, parent, token)
        conn.commit()
        notify(conn)
    print(f'Imported {count} reviews')


if __name__ == '__main__':
    main()
