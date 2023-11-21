from flask import Flask, request, render_template, redirect, url_for
import os
import narrator

app = Flask(__name__)
UPLOAD_FOLDER = 'video_source'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            return redirect(url_for('generate_video', video_path=filepath))

    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_video():
    video_path = request.args.get('video_path')
    # Call the processing function from narrator.py
    # You might need to adjust this part based on your actual processing function
    narrator.process_video(video_path)
    return 'Video processing started. Please wait...'

if __name__ == '__main__':
    app.run(debug=True)  # Set debug=False in a production environment