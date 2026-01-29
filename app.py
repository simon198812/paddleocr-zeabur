from flask import Flask, request, jsonify
from flask_cors import CORS
from paddleocr import PaddleOCR
import base64
import io
from PIL import Image
import os

app = Flask(__name__)

# 啟用 CORS，允許所有來源訪問
CORS(app)

print("正在初始化 PaddleOCR...")
ocr = PaddleOCR(use_angle_cls=True, lang='chinese_cht', use_gpu=False)
print("PaddleOCR 初始化完成！")

@app.route('/', methods=['GET'])
def home():
    """首頁，顯示服務狀態"""
    return jsonify({
        "service": "PaddleOCR API",
        "status": "running",
        "version": "1.0",
        "endpoints": {
            "/health": "健康檢查",
            "/ocr": "OCR 識別（POST 請求）"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """健康檢查接口"""
    return jsonify({"status": "ok"})

@app.route('/ocr', methods=['POST', 'OPTIONS'])
def ocr_image():
    """OCR 識別接口"""
    # 處理 OPTIONS 預檢請求
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # 檢查是否有上傳的文件
        if 'file' in request.files:
            file = request.files['file']
            image = Image.open(file.stream)
            temp_path = '/tmp/temp_image.jpg'
            image.save(temp_path)
        
        # 或者接收 base64 編碼的圖片
        elif request.json and 'image' in request.json:
            image_data = base64.b64decode(request.json['image'])
            image = Image.open(io.BytesIO(image_data))
            temp_path = '/tmp/temp_image.jpg'
            image.save(temp_path)
        
        else:
            return jsonify({
                'success': False, 
                'error': '請上傳圖片文件或提供 base64 圖片數據'
            }), 400
        
        # 執行 OCR 識別
        print(f"正在識別圖片: {temp_path}")
        result = ocr.ocr(temp_path, cls=True)
        
        # 格式化結果
        texts = []
        if result and result[0]:
            for line in result[0]:
                texts.append({
                    'text': line[1][0],
                    'confidence': float(line[1][1]),
                    'box': line[0]
                })
        
        # 清理臨時文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'count': len(texts),
            'data': texts
        })
        
    except Exception as e:
        print(f"錯誤: {str(e)}")
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"服務啟動在端口: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

