import urllib.request
import urllib.error
import traceback

urls = [
    'http://127.0.0.1:8000/',
    'http://127.0.0.1:8000/accounts/login/',
    'http://127.0.0.1:8000/accounts/signup/',
    'http://127.0.0.1:8000/modulos/',
    'http://127.0.0.1:8000/usuarios/',
    'http://127.0.0.1:8000/reportes/',
]

for url in urls:
    print('\n-----', url, '-----')
    try:
        with urllib.request.urlopen(url) as f:
            print('STATUS', f.status)
            body = f.read(5000).decode('utf-8', errors='replace')
            print(body[:1000])
    except urllib.error.HTTPError as e:
        print('HTTPError', e.code)
        try:
            print(e.read().decode('utf-8', errors='replace')[:1000])
        except Exception:
            pass
    except Exception:
        traceback.print_exc()
