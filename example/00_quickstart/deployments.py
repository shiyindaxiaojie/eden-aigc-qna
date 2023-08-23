import openai
import requests
import env

url = openai.api_base + "/openai/deployments?api-version=2022-12-01"

r = requests.get(url, headers={"api-key": env.API_KEY})

print(r.text)