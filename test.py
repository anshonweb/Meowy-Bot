import requests

# URL of the TraceMoe API
url = "https://api.trace.moe/search"

# Path to the image file you want to search
image_path = "image1.jpg"

# Open the image file in binary mode
with open(image_path, "rb") as image_file:
    # Send the image in a POST request
    response = requests.post(url, files={"image": image_file})

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    results = data['result']

    # Check if there are enough results to show the second and third
    if len(results) > 2:
        second_result = results[1]
        third_result = results[2]

        # Print information about the second result
        print("Second Result:")
        print(f"Anime Title: {second_result['filename']}")
        print(f"Episode: {second_result['episode']}")
        print(f"From: {second_result['from']} seconds")
        print(f"Similarity: {second_result['similarity']:.2f}")
        print(f"Video URL: {second_result['video']}")
        print(f"Image URL: {second_result['image']}")
        print()

        # Print information about the third result
        print("Third Result:")
        print(f"Anime Title: {third_result['filename']}")
        print(f"Episode: {third_result['episode']}")
        print(f"From: {third_result['from']} seconds")
        print(f"Similarity: {third_result['similarity']:.2f}")
        print(f"Video URL: {third_result['video']}")
        print(f"Image URL: {third_result['image']}")
    else:
        print("Not enough results returned by the API.")
else:
    print("Error:", response.status_code, response.text)



#USER_ID = '744729824400244758'
#TOKEN = 'MTI0NjUyNjE3MjA4NzU4Njg0OA.GBj7WA.uDa0jXfZNk9SgNHP0NV92anw3kYVgjJk9BpDwM'