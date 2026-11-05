"""Autenticação e consulta de avaliações do Google."""
import json
import os
import urllib.parse
import urllib.request


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


def access_token():
    if os.getenv('GOOGLE_REFRESH_TOKEN'):
        body = urllib.parse.urlencode({
            'client_id': os.environ['GOOGLE_CLIENT_ID'],
            'client_secret': os.environ['GOOGLE_CLIENT_SECRET'],
            'refresh_token': os.environ['GOOGLE_REFRESH_TOKEN'],
            'grant_type': 'refresh_token',
        }).encode()
        with urllib.request.urlopen('https://oauth2.googleapis.com/token', body, timeout=30) as response:
            return json.load(response)['access_token']
    return os.environ['GOOGLE_ACCESS_TOKEN']


