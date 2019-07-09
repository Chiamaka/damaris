import markdown
import os
import re
from flask import Flask, jsonify, request
from werkzeug import secure_filename
from . import transcribe_audio
from . import constants

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] \
        in constants.ALLOWED_EXTENSIONS


def validate_email(email):
    return re.search(constants.EMAIL_REGEX, email, re.I)


@app.route("/")
def index():
    """Present some documentation"""

    with open(os.path.dirname(app.root_path) + '/README.md', 'r') as markdown_file:
        content = markdown_file.read()
        # convert to HTML
    return markdown.markdown(content)


@app.route("/transcribe-audio", methods=('GET', 'POST'))
def transcribe():
    """
        POST: get the audio file and email and pass to transcribe function
        GET: health check for path
    """
    if request.method == 'POST':
        try:
            file = request.files['audio_file']
        except KeyError:
            file = None
        try:
            email = request.form['email_address']
        except KeyError:
            email = None

        if file is None:
            err = jsonify(
                {'status_code': 400, 'message': 'Missing audio file'})
            return err, 400
        elif not allowed_file(file.filename):
            err = jsonify({'status_code': 400, 'message': 'Bad audio file type. \
                Expects {}'.format(
                constants.ALLOWED_EXTENSIONS)})
            return err, 400
        elif email is None:
            err = jsonify({'status_code': 400, 'message': 'Missing email'})
            return err, 400
        elif validate_email(email) is None:
            err = jsonify({'status_code': 400, 'message': 'Bad email'})
            return err, 400
        else:
            filename = secure_filename(file.filename)
            # This is an easy way to achieve uniqueness for the audios uploaded
            file.save(os.path.join(
                constants.UPLOAD_FOLDER, email + '-' + filename))
            transcribe_audio.main(filename, email)
            return jsonify({'file_uploaded': 'success'})

    if request.method == 'GET':
        return jsonify({'status_code': 200, 'message': 'ok'})
