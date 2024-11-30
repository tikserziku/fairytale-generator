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

        document.getElementById('story-image').src = data.image_url;
        document.getElementById('story-text').textContent = data.story;
        
        const audioPlayer = document.getElementById('audio-player');
        audioPlayer.src = data.audio_path;
        audioPlayer.load(); // Перезагружаем аудио после изменения источника
        
        resultSection.style.display = 'block';
    } catch (error) {
        console.error('Error:', error);
        alert(`Произошла ошибка: ${error.message}`);
    } finally {
        generateBtn.disabled = false;
        loading.style.display = 'none';
    }
});