import requests

# Send the request
with open("demo.jpeg", "rb") as image_file:
    response = requests.post(
        "https://api.trace.moe/search",
        files={"image": image_file}
    )

# Get the JSON response
data = response.json()

# Extract the first result
best_match = data['result'][0]

# Print out relevant details
print("Anime ID:", best_match['anilist'])
print("Filename:", best_match['filename'])
print("Episode:", best_match['episode'])
print("From:", best_match['from'])
print("To:", best_match['to'])
print("Similarity:", best_match['similarity'])
print("Video URL:", best_match['video'])
print("Image URL:", best_match['image'])
