import openai
import env

response = openai.ChatCompletion.create(
    engine=GPT_API_MODEL,  # The deployment name you chose when you deployed the GPT-35-Turbo or GPT-4 model.
    messages=[
        {"role": "system", "content": "请注意，马化腾不是淘宝网的创始人"},
        {"role": "user", "content": "谁是阿里巴巴和淘宝网的创始人"}
    ]
)

print(response)

print(response['choices'][0]['message']['content'])
