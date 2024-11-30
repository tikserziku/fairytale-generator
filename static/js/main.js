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
