import requests

# API
API_URL = "https://api-inference.huggingface.co/models/peter2000/xlm-roberta-base-finetuned-ecoicop"
API_TOKEN = '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'
headers = {"Authorization": f"Bearer {API_TOKEN}"}


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def find(name: str, category: str) -> list:
    # API with product
    output = query({"inputs": f"{name} | {category} |", })

    # Get Category from API with highest score
    score = 0
    label = ''
    for i in range(len(output[0])):

        if float(output[0][i].get('score')) > score:
            score = output[0][i].get('score')
            label = output[0][i].get('label')

    # Return results as list
    return [label, score]
