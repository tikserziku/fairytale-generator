document.getElementById('story-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const topic = document.getElementById('topic').value;
    const age = document.getElementById('age').value;
    const formData = new FormData();
    formData.append('topic', topic);
    formData.append('age', age);

    const generateBtn = document.getElementById('generate-btn');
    const loading = document.getElementById('loading');
    const resultSection = document.getElementById('result-section');
    
    generateBtn.disabled = true;
    loading.style.display = 'block';
    resultSection.style.display = 'none';

    try {
        // Отправляем запрос на генерацию
        const response = await fetch('/generate', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        // Проверяем статус каждые 2 секунды
        const checkStatus = async () => {
            const statusResponse = await fetch(`/status/${data.request_id}`);
            const statusData = await statusResponse.json();
            
            if (statusData.status === 'complete') {
                document.getElementById('story-image').src = statusData.image_url;
                document.getElementById('story-text').textContent = statusData.story;
                document.getElementById('audio-player').src = statusData.audio_path;
                resultSection.style.display = 'block';
                loading.style.display = 'none';
                generateBtn.disabled = false;
                return;
            } else if (statusData.status === 'error') {
                throw new Error(statusData.error);
            }
            
            // Продолжаем проверять
            setTimeout(checkStatus, 2000);
        };
        
        checkStatus();
        
    } catch (error) {
        console.error('Error:', error);
        alert(`Произошла ошибка: ${error.message}`);
        loading.style.display = 'none';
        generateBtn.disabled = false;
    }
});