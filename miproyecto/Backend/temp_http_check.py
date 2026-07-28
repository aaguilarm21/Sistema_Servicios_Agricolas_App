import urllib.request
import urllib.error
import traceback

url = 'http://127.0.0.1:8000/'
try:
    with urllib.request.urlopen(url) as f:
        print('STATUS', f.status)
        print(f.read(2000).decode('utf-8', errors='replace'))
except urllib.error.HTTPError as e:
    print('HTTPError', e.code)
    print(e.read().decode('utf-8', errors='replace'))
except Exception:
    traceback.print_exc()
