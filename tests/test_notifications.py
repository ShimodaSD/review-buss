import sys
import io
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'data/scrapping/reviews'))
import google
import telegram


class NotificationTest(unittest.TestCase):
    def test_refresh_token(self):
        class Response(io.BytesIO):
            pass
        with patch.dict(os.environ, {'GOOGLE_REFRESH_TOKEN': 'refresh', 'GOOGLE_CLIENT_ID': 'id', 'GOOGLE_CLIENT_SECRET': 'secret'}), patch.object(google.urllib.request, 'urlopen', return_value=Response(b'{"access_token":"fresh"}')):
            self.assertEqual(google.access_token(), 'fresh')

    def test_telegram_failure_does_not_mark_sent(self):
        class Cursor:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def execute(self, *args):
                if args[0].startswith('UPDATE'):
                    self.updated = True
            def fetchone(self): return ('id', 'Ana', 'FIVE', 'Bom')
        class Connection:
            def __init__(self): self.cur = Cursor()
            def transaction(self): return self.cur
            def cursor(self): return self.cur
        conn = Connection()
        with patch.dict(os.environ, {'TELEGRAM_CHAT_ID': '1', 'TELEGRAM_BOT_TOKEN': 'token'}), patch.object(telegram.urllib.request, 'urlopen', return_value=io.BytesIO(json.dumps({'ok': False}).encode())):
            with self.assertRaises(RuntimeError): telegram.notify(conn)
        self.assertFalse(getattr(conn.cur, 'updated', False))


if __name__ == '__main__':
    unittest.main()
