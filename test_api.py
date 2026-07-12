import urllib.request
import urllib.error
import json

part1 = "AQ.Ab8RN6Ki_DiQsUjU"
part2 = "mGRWl9-V1IEiahLgRORsjWm7CqFwldG7GA"
api_key = part1 + part2

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

req = urllib.request.Request(url)
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        models = [m['name'] for m in data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
        print("Available models:", models)
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode()}")
except Exception as e:
    print("Error:", e)
