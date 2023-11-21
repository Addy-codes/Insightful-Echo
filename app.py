from flask import Flask, request, render_template, send_from_directory, abort
import os
import narrator

app = Flask(__name__)
UPLOAD_FOLDER = 'video_source'
PROCESSED_FOLDER = 'processed_videos'  # Assuming processed videos are stored here
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

# Ensure both upload and processed folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return 'No file part in the request'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            generate_video(video_path=filepath)

    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_video(video_path):
    # Call the processing function from narrator.py
    # Adjust this part to handle the processing and store the processed video in PROCESSED_FOLDER
    processed_video_path = narrator.process_video(video_path)
    return 'Processing started'  # Adjust as needed

@app.route('/download')
def download_file():
    filename = 'output_sample.mp4'
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)  # Set debug=False in a production environment
