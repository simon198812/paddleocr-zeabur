FROM python:3.8-slim  
LABEL "language"="python"  
RUN apt-get update && apt-get install -y \  
    libgomp1 \  
    libglib2.0-0 \  
    libsm6 \  
    libxext6 \  
    libxrender-dev \  
    libgl1-mesa-glx \  
    && rm -rf /var/lib/apt/lists/*  
WORKDIR /app  
COPY requirements.txt .  
RUN pip install --no-cache-dir -r requirements.txt  
RUN python -c "from paddleocr import PaddleOCR; PaddleOCR(use_angle_cls=True, lang='chinese_cht', use_gpu=False)"  
COPY . .  
EXPOSE 8080  
CMD ["python", "app.py"]  
