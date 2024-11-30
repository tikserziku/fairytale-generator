from flask import Flask, render_template, request, jsonify
import openai
import os
from dotenv import load_dotenv
import logging

load_dotenv()
app = Flask(__name__)

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Исправленная инициализация OpenAI клиента
try:
    client = openai.Client(api_key=os.getenv('OPENAI_API_KEY'))
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    client = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        if not client:
            raise Exception("OpenAI client not initialized")
        
        if not os.getenv('OPENAI_API_KEY'):
            raise Exception("OPENAI_API_KEY not set")

        topic = request.form.get('topic')
        age = request.form.get('age')
        
        if not topic or not age:
            raise ValueError("Topic and age are required")

        # Генерация сказки
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Используем более доступную модель
            messages=[
                {
                    "role": "system",
                    "content": f"Напиши добрую сказку для детей возраста {age} лет на тему {topic}."
                }
            ]
        )
        story = completion.choices[0].message.content

        # Генерация изображения
        image_response = client.images.generate(
            prompt=f"Детская иллюстрация к сказке про {topic}, мультяшный стиль",
            n=1,
            size="1024x1024"
        )
        image_url = image_response.data[0].url

        # Генерация аудио
        speech_file = os.path.join('static', 'temp_audio.mp3')
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=story
        )

        # Создаем директорию static, если её нет
        os.makedirs('static', exist_ok=True)
        
        # Сохраняем аудио
        response.stream_to_file(speech_file)

        return jsonify({
            'story': story,
            'image_url': image_url,
            'audio_path': '/static/temp_audio.mp3'
        })
        
    except Exception as e:
        logger.error(f"Error in generate: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)