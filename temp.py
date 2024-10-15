import os
import requests

# Function to check if the OpenAI API key is valid
def check_openai_api_key(api_key):
    url = "https://api.openai.com/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # Send a request to OpenAI's models API endpoint
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("API key is valid.")
        print("Available models:", response.json())
    elif response.status_code == 401:
        print("Invalid API key. Please check your API key and try again.")
    else:
        print(f"Failed to connect to the API. Status code: {response.status_code}.")
        print("Response:", response.text)

# Example: Replace this with your actual OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY", "sk-1TExnFaWRMte1BeuLYYd5bOOrnte3jUcGhU8a5_SQqT3BlbkFJKGZkCnuJsUXgp1aRmY221YMEVmY-jzHJPOTpUjVZsA")

# Check if the API key is valid
check_openai_api_key(openai_api_key)
