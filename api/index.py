from flask import Flask, request, jsonify
import json
import urllib.request
import urllib.parse
import unicodedata

app = Flask(__name__)

INDEX_URL = "https://raw.githubusercontent.com/Coarsey/xiaozhi-music/main/index.json"

def remove_accents(input_str):
    if not input_str:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

@app.route('/api', methods=['GET'])
@app.route('/', methods=['GET'])
def search_music():
    raw_keyword = request.args.get('q', '').strip()
    clean_keyword = remove_accents(raw_keyword)

    if not clean_keyword:
        return jsonify({"status": "error", "message": "Vui lòng nhập từ khóa ?q="}), 400

    try:
        req = urllib.request.Request(INDEX_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            songs = json.loads(response.read().decode('utf-8'))

        for song in songs:
            song_name = remove_accents(song.get('name', ''))
            song_id = remove_accents(song.get('id', ''))
            song_tags = [remove_accents(t) for t in song.get('tags', [])]
            
            if clean_keyword in song_name or clean_keyword == song_id or any(clean_keyword in tag for tag in song_tags):
                raw_path = song['path']
                encoded_path = urllib.parse.quote(raw_path)
                full_url = f"https://raw.githubusercontent.com/Coarsey/xiaozhi-music/main/{encoded_path}"
                
                return jsonify({
                    "status": "success",
                    "name": song['name'],
                    "url": full_url
                })

        return jsonify({
            "status": "not_found",
            "message": f"Không tìm thấy bài hát nào cho từ khóa: {raw_keyword}"
        }), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500