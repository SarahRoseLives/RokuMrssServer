import sqlite3
import uuid
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

db_name = 'file_database.db'

# Create SQLite database and table if not exists
conn = sqlite3.connect(db_name)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        language TEXT,
        lastUpdated TEXT,
        providerName TEXT,
        adBreaks TEXT,
        captions TEXT,
        dateAdded TEXT,
        duration INTEGER,
        videoQuality TEXT,
        videoUrl TEXT,
        videoType TEXT,
        genres TEXT,
        fileId TEXT,
        rating TEXT,
        ratingSource TEXT,
        releaseDate TEXT,
        shortDescription TEXT,
        tags TEXT,
        thumbnail TEXT,
        title TEXT,
        guid TEXT UNIQUE,
        pubDate TEXT,
        mediaTitle TEXT,
        mediaDescription TEXT,
        mediaCategory TEXT,
        mediaThumbnail TEXT,
        mediaContent_url TEXT,
        mediaContent_duration TEXT,
        mediaContent_bitrate TEXT,
        mediaContent_language TEXT,
        mediaSubTitle_lang TEXT,
        mediaSubTitle_href TEXT
    )
''')
conn.commit()
conn.close()


# New route to display the form for adding files
@app.route('/add_file', methods=['GET'])
def show_add_file_form():
    return render_template('add_file.html')

# Modify the add_file route to handle form submission
@app.route('/add_file', methods=['POST'])
def add_file():
    # Parse form data
    media_title = request.form.get('mediaTitle')
    media_description = request.form.get('mediaDescription')
    media_category = request.form.get('mediaCategory')
    media_thumbnail = request.form.get('mediaThumbnail')
    media_content_url = request.form.get('mediaContentUrl')
    media_content_duration = request.form.get('mediaContentDuration', '')  # Defaults to empty string if not provided
    media_content_bitrate = request.form.get('mediaContentBitrate', '')  # Defaults to empty string if not provided
    media_content_language = request.form.get('mediaContentLanguage', '')  # Defaults to empty string if not provided
    media_subtitle_lang = request.form.get('mediaSubTitleLang', '')  # Defaults to empty string if not provided
    media_subtitle_href = request.form.get('mediaSubTitleHref', '')  # Defaults to empty string if not provided

    # Validate form data (add your validation logic here)

    # Your existing code for adding files...
    if media_title and media_description and media_category and media_thumbnail and media_content_url:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Modify the guid value generation
        guid_value = str(uuid.uuid4())

        try:
            cursor.execute('''
                INSERT INTO files (
                    guid, pubDate, mediaTitle, mediaDescription, mediaCategory, mediaThumbnail,
                    mediaContent_url, mediaContent_duration, mediaContent_bitrate,
                    mediaContent_language, mediaSubTitle_lang, mediaSubTitle_href
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                guid_value, "2022-01-16T12:00:00Z", media_title, media_description, media_category, media_thumbnail,
                media_content_url, media_content_duration, media_content_bitrate, media_content_language,
                media_subtitle_lang, media_subtitle_href
            ))

            conn.commit()
            conn.close()
            return jsonify({"message": "File added successfully"})
        except Exception as e:
            conn.rollback()
            conn.close()
            return jsonify({"error": str(e)}), 400
    else:
        return jsonify({"error": "Invalid payload"}), 400



@app.route('/generate_feed', methods=['GET'])
def generate_feed():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            language, pubDate, mediaTitle, mediaDescription, mediaCategory,
            mediaThumbnail, mediaContent_url, mediaContent_duration,
            mediaContent_bitrate, mediaContent_language,
            mediaSubTitle_lang, mediaSubTitle_href
        FROM files
    ''')

    files = cursor.fetchall()
    conn.close()

    file_entries = []

    for file in files:
        video_entry = {
            "id": file[10],  # Assuming 'guid' is unique and can be used as an ID
            "title": file[2] if file[2] else "",
            "shortDescription": file[3] if file[3] else "",
            "thumbnail": file[5] if file[5] else "",
            "genres": [file[4] if file[4] else ""],
            "tags": [file[4] if file[4] else ""],
            "releaseDate": file[1] if file[1] else "",
            "content": {
                "dateAdded": "",
                "captions": [],
                "duration": int(file[7]) if file[7] else 0,
                "adBreaks": ["00:00:00"],  # Assuming ad breaks start at the beginning
                "videos": [
                    {
                        "url": file[6] if file[6] else "",
                        "quality": "HD",
                        "videoType": "MP4"
                    }
                ]
            },
            "language": "en-us",
            "rating": {
                "rating": "G",
                "ratingSource": "USA_PR"
            }
        }
        file_entries.append(video_entry)

    feed = {
        "providerName": "Your Provider Name",
        "language": "en-US",
        "lastUpdated": "2024-01-16T12:00:00Z",
        "shortFormVideos": file_entries,
        "playlists": [
            {
                "name": "all_videos",
                "itemIds": [video["id"] for video in file_entries]
            }
            # Add more playlists if needed
        ],
        "categories": [
            {
                "name": "All Videos",
                "playlistName": "all_videos",
                "order": "manual"
            }
            # Add more categories if needed
        ]
    }

    # Additional categories for specific genres
    for genre in set([file[4] for file in files if file[4]]):
        category_name = genre.lower().replace(' ', '_') + "_videos"
        category_playlist = {
            "name": category_name,
            "itemIds": [video["id"] for video in file_entries if genre in video["genres"]]
        }
        feed["playlists"].append(category_playlist)

        category_entry = {
            "name": genre,
            "playlistName": category_name,
            "order": "manual"
        }
        feed["categories"].append(category_entry)

    return jsonify(feed)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
