import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

@app.route("/")
def home():
    return jsonify({
        "app": "RHYTHM MUSIC API",
        "status": "running"
    })

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Song name is required"}), 400

    if not API_KEY:
        return jsonify({"error": "Server API key is not configured"}), 500

    try:
        response = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": query,
                "type": "video",
                "videoCategoryId": "10",
                "maxResults": 20,
                "key": API_KEY
            },
            timeout=20
        )

        data = response.json()

        if response.status_code != 200:
            return jsonify({
                "error": data.get("error", {}).get(
                    "message", "YouTube search failed"
                )
            }), response.status_code

        songs = []

        for item in data.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            snippet = item.get("snippet", {})

            if not video_id:
                continue

            songs.append({
                "id": video_id,
                "title": snippet.get("title", ""),
                "artist": snippet.get("channelTitle", ""),
                "thumb": snippet.get("thumbnails", {}).get(
                    "medium", {}
                ).get("url", ""),
                "url": "https://www.youtube.com/watch?v=" + video_id
            })

        return jsonify({"results": songs})

    except requests.RequestException:
        return jsonify({"error": "Could not contact YouTube"}), 502

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
