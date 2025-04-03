import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc0MzcwODM0Mn0.BKX6JeRkitbhQ9VQ2xjLQ2w8tDSoUMi-Ou-TtEUAr_c"  # Replace with a valid token
video_path = "/Users/somnathmahato/Downloads/My Video-highlight.mp4"

headers = {
    "Authorization": f"Bearer {token}"
}

files = {
    "file": open(video_path, "rb")
}

if __name__ == "__main__":
    response = requests.post("http://127.0.0.1:8000/upload/", headers=headers, files=files)
    print(response.json())  # Should return {"filename": "video.mp4", "status": "Uploaded"}