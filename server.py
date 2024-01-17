import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates')

# Database to store files
file_database = []

# Function to generate MRSS feed URL
# Update the generate_feed_url function in your server.py



def generate_feed_url():
    feed_data = {
        "providerName": "Your Provider Name",
        "language": "en-US",
        "lastUpdated": "2024-01-16T12:00:00Z",  # Update with the current date and time
        "shortFormVideos": []
    }

    for file_entry in file_database:
        feed_item = {
            "id": file_entry.get("mediaID", ""),
            "title": file_entry.get("mediaTitle", ""),
            "shortDescription": file_entry.get("mediaDescription", ""),
            "thumbnail": file_entry.get("mediaThumbnail", ""),
            "genres": [file_entry.get("mediaCategory", "")],
            "tags": file_entry.get("mediaTags", "").split(','),
            "releaseDate": file_entry.get("mediaReleaseDate", ""),
            "content": {
                "dateAdded": file_entry.get("mediaDateAdded", ""),
                "captions": [],
                "duration": int(file_entry.get("mediaDuration", 0)) if file_entry.get("mediaDuration", "") else 0,
                "adBreaks": ["00:00:00", "00:{}".format(file_entry.get("mediaDuration", ""))],
                "videos": [{
                    "url": file_entry.get("mediaContent", {}).get("url", ""),
                    "quality": "HD",  # Adjust based on your channel's requirements
                    "videoType": "MP4"  # Adjust based on your channel's requirements
                }]
            },
            "language": "en-us",
            "rating": {
                "rating": "G",
                "ratingSource": "USA_PR"
            }
        }

        feed_data["shortFormVideos"].append(feed_item)

    return jsonify(feed_data)

# Endpoint to add a file to the database
# Endpoint to add a file to the database
@app.route('/add_file', methods=['POST'])
def add_file():
    data = request.get_json()

    # Assuming the JSON payload contains the required fields
    media_title = data.get('mediaTitle')
    media_description = data.get('mediaDescription')
    media_category = data.get('mediaCategory')
    thumbnail_url = data.get('thumbnailUrl')
    video_url = data.get('videoUrl')
    video_duration = data.get('videoDuration')
    sub_title_url = data.get('subTitleUrl')

    if media_title and media_description and media_category and thumbnail_url and video_url and video_duration:
        file_entry = {
            "guid": video_url,  # Assuming video_url can be used as a unique identifier
            "pubDate": "2022-01-16T12:00:00Z",  # Update with the current date and time
            "mediaTitle": media_title,
            "mediaDescription": media_description,
            "mediaCategory": media_category,
            "mediaThumbnail": thumbnail_url,
            "mediaContent": {
                "url": video_url,
                "duration": video_duration,
                "bitrate": "2500",  # You can customize this based on your file quality
                "language": "en-us"  # Adjust based on your file language
            },
            "mediaSubTitle": {
                "lang": "en-us",
                "href": sub_title_url
            } if sub_title_url else None
        }

        file_database.append(file_entry)
        return jsonify({"message": "File added successfully"})
    else:
        return jsonify({"error": "Invalid payload"}), 400
# Endpoint to get the MRSS feed URL
@app.route('/generate_feed', methods=['GET'])
def generate_feed():
    return generate_feed_url()

# Default route to render the HTML form
@app.route('/')
def index():
    return render_template('add_file.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
