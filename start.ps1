# Создаем основную директорию
$baseDir = "G:\Claude_Pasaka"
New-Item -ItemType Directory -Force -Path $baseDir

# Создаем структуру проекта
$dirs = @(
    "$baseDir\static",
    "$baseDir\static\css",
    "$baseDir\static\js",
    "$baseDir\templates"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir
}

# requirements.txt
@"
flask==2.0.1
openai==1.3.0
python-dotenv==0.19.0
gunicorn==20.1.0
"@ | Out-File -FilePath "$baseDir\requirements.txt" -Encoding utf8

# Procfile для Heroku
@"
web: gunicorn app:app
"@ | Out-File -FilePath "$baseDir\Procfile" -Encoding utf8

# .gitignore
@"
__pycache__/
*.pyc
.env
.venv
env/
venv/
ENV/
"@ | Out-File -FilePath "$baseDir\.gitignore" -Encoding utf8

# app.py
@"
from flask import Flask, render_template, request, jsonify
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    topic = request.form.get('topic')
    age = request.form.get('age')
    
    # Генерация сказки через OpenAI
    story_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": f"Напиши добрую сказку для детей возраста {age} лет на тему {topic}."
            }
        ]
    )
    story = story_response.choices[0].message.content

    # Генерация изображения
    image_response = openai.Image.create(
        prompt=f"Детская иллюстрация к сказке про {topic}",
        n=1,
        size="1024x1024"
    )
    image_url = image_response['data'][0]['url']

    # Генерация аудио
    audio_response = openai.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=story
    )
    
    # Сохраняем аудио во временный файл
    audio_path = "static/temp_audio.mp3"
    audio_response.stream_to_file(audio_path)

    return jsonify({
        'story': story,
        'image_url': image_url,
        'audio_path': audio_path
    })

if __name__ == '__main__':
    app.run(debug=True)
"@ | Out-File -FilePath "$baseDir\app.py" -Encoding utf8

# static/css/style.css
@"
body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 20px;
    background-color: #f0f8ff;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}

.story-image {
    width: 100%;
    max-height: 400px;
    object-fit: cover;
    border-radius: 10px;
    margin-bottom: 20px;
}

.form-group {
    margin-bottom: 20px;
}

label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

input, select {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

button {
    background-color: #4CAF50;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background-color: #45a049;
}

#story-text {
    margin-top: 20px;
    white-space: pre-wrap;
}

.audio-player {
    width: 100%;
    margin: 20px 0;
}
"@ | Out-File -FilePath "$baseDir\static\css\style.css" -Encoding utf8

# static/js/main.js
@"
document.getElementById('story-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const topic = document.getElementById('topic').value;
    const age = document.getElementById('age').value;
    const formData = new FormData();
    formData.append('topic', topic);
    formData.append('age', age);

    document.getElementById('generate-btn').disabled = true;
    document.getElementById('loading').style.display = 'block';

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        document.getElementById('story-image').src = data.image_url;
        document.getElementById('story-text').textContent = data.story;
        document.getElementById('audio-player').src = data.audio_path;
        
        document.getElementById('result-section').style.display = 'block';
    } catch (error) {
        console.error('Error:', error);
        alert('Произошла ошибка при генерации сказки');
    } finally {
        document.getElementById('generate-btn').disabled = false;
        document.getElementById('loading').style.display = 'none';
    }
});
"@ | Out-File -FilePath "$baseDir\static\js\main.js" -Encoding utf8

# templates/index.html
@"
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Генератор Сказок</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>Генератор Сказок</h1>
        
        <form id="story-form">
            <div class="form-group">
                <label for="topic">О чем сказка?</label>
                <input type="text" id="topic" required>
            </div>
            
            <div class="form-group">
                <label for="age">Возраст детей:</label>
                <select id="age" required>
                    <option value="3-5">3-5 лет</option>
                    <option value="6-8">6-8 лет</option>
                    <option value="9-12">9-12 лет</option>
                </select>
            </div>
            
            <button type="submit" id="generate-btn">Создать сказку</button>
        </form>

        <div id="loading" style="display: none;">
            Генерируем сказку...
        </div>

        <div id="result-section" style="display: none;">
            <img id="story-image" class="story-image" alt="Иллюстрация к сказке">
            
            <audio id="audio-player" controls class="audio-player">
                <source src="" type="audio/mpeg">
                Ваш браузер не поддерживает аудио элемент.
            </audio>
            
            <div id="story-text"></div>
        </div>
    </div>
    
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
"@ | Out-File -FilePath "$baseDir\templates\index.html" -Encoding utf8 -Force

# .env
@"
OPENAI_API_KEY=your-api-key-here
"@ | Out-File -FilePath "$baseDir\.env" -Encoding utf8

Write-Host "Проект успешно создан в директории $baseDir"