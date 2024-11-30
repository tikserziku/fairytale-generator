from flask import Flask, render_template, request, jsonify
import openai
import groq
import os
from dotenv import load_dotenv
import logging
import threading
import time

load_dotenv()
app = Flask(__name__)

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализируем клиентов
openai_client = openai.Client(api_key=os.getenv('OPENAI_API_KEY'))
groq_client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))

# Хранилище результатов
results = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        topic = request.form.get('topic')
        age = request.form.get('age')
        
        # Генерируем ID запроса
        request_id = f"{time.time()}"
        
        # Запускаем асинхронную генерацию
        threading.Thread(
            target=generate_content,
            args=(request_id, topic, age)
        ).start()
        
        return jsonify({
            'request_id': request_id,
            'status': 'processing'
        })
        
    except Exception as e:
        logger.error(f"Error in generate: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

def generate_content(request_id, topic, age):
    try:
        logger.info(f"Generating story for topic: {topic}, age: {age}")
        
        # Генерация сказки через Groq
        story_completion = groq_client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": f"Напиши добрую сказку для детей возраста {age} лет на тему {topic}."
            }],
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=2048
        )
        story = story_completion.choices[0].message.content

        # Генерация изображения через OpenAI (так как Groq не поддерживает генерацию изображений)
        image_response = openai_client.images.generate(
            prompt=f"Детская иллюстрация к сказке про {topic}, мультяшный стиль",
            n=1,
            size="1024x1024"
        )
        image_url = image_response.data[0].url

        # Создаем директорию static, если её нет
        os.makedirs('static', exist_ok=True)

        # Генерация аудио через OpenAI
        speech_file = os.path.join('static', f'audio_{request_id}.mp3')
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=story
        )
        
        # Сохраняем аудио
        response.stream_to_file(speech_file)
        
        # Сохраняем результат
        results[request_id] = {
            'complete': True,
            'story': story,
            'image_url': image_url,
            'audio_path': f'/static/audio_{request_id}.mp3'
        }
        
        logger.info("Successfully generated story, image and audio")
        
    except Exception as e:
        logger.error(f"Error in generate_content: {str(e)}")
        results[request_id] = {'error': str(e)}

@app.route('/status/<request_id>', methods=['GET'])
def check_status(request_id):
    if request_id in results:
        result = results[request_id]
        if 'error' in result:
            return jsonify({'status': 'error', 'error': result['error']})
        if 'complete' in result:
            data = results.pop(request_id)
            return jsonify({
                'status': 'complete',
                'story': data['story'],
                'image_url': data['image_url'],
                'audio_path': data['audio_path']
            })
        return jsonify({'status': 'processing'})
    return jsonify({'status': 'not_found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)