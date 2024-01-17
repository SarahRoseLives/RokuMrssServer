import sqlite3
from flask import Flask, request, jsonify

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


def add_file():
    data = request.get_json()

    # Assuming the JSON payload contains the required fields
    media_title = data.get('mediaTitle')
    media_description = data.get('mediaDescription')
    media_category = data.get('mediaCategory')
    thumbnail_url = data.get('mediaThumbnail')
    video_url = data.get('mediaContent').get('url')
    video_duration = data.get('mediaContent').get('duration')
    video_bitrate = data.get('mediaContent').get('bitrate')
    video_language = data.get('mediaContent').get('language')
    subtitle_lang = data.get('mediaSubTitle').get('lang') if data.get('mediaSubTitle') else None
    subtitle_href = data.get('mediaSubTitle').get('href') if data.get('mediaSubTitle') else None

    if media_title and media_description and media_category and thumbnail_url and video_url and video_duration:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO files (
                    guid, pubDate, mediaTitle, mediaDescription, mediaCategory, mediaThumbnail,
                    mediaContent_url, mediaContent_duration, mediaContent_bitrate,
                    mediaContent_language, mediaSubTitle_lang, mediaSubTitle_href
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_url, "2022-01-16T12:00:00Z", media_title, media_description, media_category, thumbnail_url,
                video_url, video_duration, video_bitrate, video_language, subtitle_lang, subtitle_href
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
