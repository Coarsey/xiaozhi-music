from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import urllib.request
import unicodedata

INDEX_URL = "https://raw.githubusercontent.com/Coarsey/xiaozhi-music/main/index.json"

# Hàm xoá dấu Tiếng Việt để so sánh chuỗi chính xác
def remove_accents(input_str):
    if not input_str:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        # Lấy từ khóa người dùng gửi lên
        raw_keyword = query_params.get('q', [''])[0].strip()
        clean_keyword = remove_accents(raw_keyword)

        result = None
        
        try:
            req = urllib.request.Request(INDEX_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                songs = json.loads(response.read().decode('utf-8'))

            if clean_keyword:
                for song in songs:
                    # Chuẩn hóa tên bài hát và id
                    song_name = remove_accents(song.get('name', ''))
                    song_id = remove_accents(song.get('id', ''))
                    song_tags = [remove_accents(t) for t in song.get('tags', [])]
                    
                    # Kiểm tra xem từ khóa có nằm trong Name, ID hoặc Tags không
                    match_name = clean_keyword in song_name
                    match_id = clean_keyword == song_id
                    match_tags = any(clean_keyword in tag for tag in song_tags)
                    
                    if match_name or match_id or match_tags:
                        # Encode lại đường dẫn URL để không bị lỗi ký tự Tiếng Việt/Khoảng trắng
                        raw_path = song['path']
                        encoded_path = urllib.parse.quote(raw_path)
                        full_url = f"https://raw.githubusercontent.com/Coarsey/xiaozhi-music/main/{encoded_path}"
                        
                        result = {
                            "status": "success",
                            "name": song['name'],
                            "url": full_url
                        }
                        break

        except Exception as e:
            result = {"status": "error", "message": str(e)}

        # Trả kết quả JSON
        self.send_response(200 if result and result.get("status") == "success" else 404)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_data = result if result else {"status": "not_found", "message": f"Không tìm thấy bài hát nào cho từ khóa: {raw_keyword}"}
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))