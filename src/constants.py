import os

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'audios')
TRANSCRIPTION_FOLDER = os.path.join(os.getcwd(), 'transcriptions')
ALLOWED_EXTENSIONS = set(['mp3'])
EMAIL_REGEX = r'\S+@\S+\.\S+'
