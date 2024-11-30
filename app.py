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
