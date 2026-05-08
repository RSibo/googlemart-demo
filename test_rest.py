import urllib.request
import json
import sys

TOKEN = "bad_token"
url = "https://us-central1-aiplatform.googleapis.com/v1beta1/projects/cloud-llm-preview1/locations/us-central1/publishers/google/models/gemini-3.1-flash-live-preview-04-2026"

req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} {e.reason}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
