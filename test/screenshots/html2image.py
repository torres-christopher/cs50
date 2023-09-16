import requests

# Define the API endpoint URL
api_url = "https://www.html2image.net/api/api.php"

# Set personal API key
api_key = "147.161.235.85"

# Set the source HTML page or raw HTML code
source_html = "https://www.google.com"  # You can also provide raw HTML code here

# Set the desired image type, width, height, quality, and zoom
params = {
    "key": api_key,
    "source": source_html,
    "type": "png",
    "width": 1200,
    "height": 600,
    "quality": 95,
    "zoom": 0.5,
}

# Send a POST request to the API
response = requests.post(api_url, data=params)

# Check if the request was successful
if response.status_code == 200:
    # Save the received image
    with open("output.png", "wb") as f:
        f.write(response.content)
    print("Image saved as 'output.png'")
else:
    print(f"Request failed with status code {response.status_code}: {response.text}")
