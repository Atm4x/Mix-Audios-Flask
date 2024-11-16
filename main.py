from flask import Flask, render_template, request, send_file
import os
from pydub import AudioSegment
import io

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def convert_volume_to_db(volume_value):
    # Преобразование значения ползунка (0-100) в дБ (-30 до +30)
    return (float(volume_value) - 50) * 0.6

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'audio_files' not in request.files:
            return 'No files uploaded'
        
        files = request.files.getlist('audio_files')
        volumes = request.form.getlist('volume')
        
        combined = None
        for i, file in enumerate(files):
            if file.filename:
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(temp_path)
                
                audio = AudioSegment.from_file(temp_path)
                
                # Получаем значение громкости в дБ
                volume_db = convert_volume_to_db(volumes[i] if i < len(volumes) else 50)
                
                # Применяем изменение громкости
                audio = audio.apply_gain(volume_db)
                
                if combined is None:
                    combined = audio
                else:
                    combined = combined.overlay(audio)
                
                os.remove(temp_path)
        
        if combined:
            buffer = io.BytesIO()
            combined.export(buffer, format='mp3')
            buffer.seek(0)
            
            return send_file(
                buffer,
                mimetype='audio/mp3',
                as_attachment=True,
                download_name='combined.mp3'
            )
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=1969)