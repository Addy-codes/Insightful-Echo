from flask import Flask, request, render_template, send_from_directory, abort
import os
import base64
import narrator

app = Flask(__name__)
UPLOAD_FOLDER = None
FILE_NAME = None
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_video():
    global UPLOAD_FOLDER, FILE_NAME
    if request.method == 'POST':
        unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
        dir_path = os.path.join("narration", unique_id)
        os.makedirs(dir_path, exist_ok=True)
        UPLOAD_FOLDER = dir_path
        # Check if the post request has the file part
        if 'file' not in request.files:
            return 'No file part in the request'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            FILE_NAME = file.filename
            generate_video(video_path=filepath)

    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_video(video_path):
    global UPLOAD_FOLDER
    # Call the processing function from narrator.py
    # Adjust this part to handle the processing and store the processed video in PROCESSED_FOLDER
    processed_video_path = narrator.process_video(video_path,UPLOAD_FOLDER)
    return 'Processing started'  # Adjust as needed

@app.route('/download')
def download_file():
    global UPLOAD_FOLDER, FILE_NAME
    filename = f'{FILE_NAME}_out.mp4'
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)  # Set debug=False in a production environment
