import requests

url = "https://api.elevenlabs.io/v1/voices"

headers = {
  "Accept": "application/json",
  "xi-api-key": "075d7fe616ce90ffeaf77b9ad06192b0"
}

response = requests.get(url, headers=headers)

print(response.text)
