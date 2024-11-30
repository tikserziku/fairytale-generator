from flask import Flask, render_template, request, jsonify
import openai
import os
from dotenv import load_dotenv
import logging

load_dotenv()
app = Flask(__name__)
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        topic = request.form.get('topic')
        age = request.form.get('age')
        
        # Генерация сказки через OpenAI
        story_response = client.chat.completions.create(
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
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=f"Детская иллюстрация к сказке про {topic}",
            n=1,
            size="1024x1024"
        )
        image_url = image_response.data[0].url

        # Генерация аудио
        audio_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=story
        )
        
        # Сохраняем аудио во временный файл
        audio_path = os.path.join('static', 'temp_audio.mp3')
        with open(audio_path, 'wb') as f:
            for chunk in audio_response.iter_bytes():
                f.write(chunk)

        return jsonify({
            'story': story,
            'image_url': image_url,
            'audio_path': '/static/temp_audio.mp3'
        })
        
    except Exception as e:
        logging.error(f"Error in generate: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)