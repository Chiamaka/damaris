import wave
import os
import re
import logging

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from . import constants

LOG_FORMAT = "%(levelname)s %(asctime)s %(message)s"
log_file = os.path.join(os.getcwd(), 'log_file.log')
logging.basicConfig(filename=log_file,
                    level=logging.DEBUG, format=LOG_FORMAT)
log = logging.getLogger(__name__)


class Transcribe:
    def __init__(self, filename, email):
        # This is an easy way to achieve uniqueness for the audios uploaded
        # eg "chi@mpharma.com-Untitled.mp3"
        self.filename = email + '-' + filename
        self.bare_filename = re.sub(r'.mp3', '', self.filename)
        self.wav_filename = '{}.wav'.format(self.bare_filename)
        self.email = email
        self.mp3_file = os.path.join(
            constants.UPLOAD_FOLDER, self.filename)
        self.wav_file = os.path.join(
            constants.UPLOAD_FOLDER, self.wav_filename)
        self.transcription_filename = os.path.join(
            constants.TRANSCRIPTION_FOLDER, '{}.txt'.format(self.bare_filename))

    def start_process(self):
        log.info('Starting....')
        self.convert_from_mp3_to_wav()
        duration = self.get_duration()

        if duration <= 60:
            log.info('Local transcription....')
            self.transcribe_file()
        else:
            log.info('Remote upload then transcription....')
            gcs_uri = self.upload_audio_file_to_google_storage()
            self.transcribe_gcs(gcs_uri)

    def get_duration(self):
        """Return the duration of the wav file"""
        with wave.open(self.wav_file, 'r') as frame:
            frames = frame.getnframes()
            rate = frame.getframerate()
            duration = frames / float(rate)
            return duration

    def convert_from_mp3_to_wav(self):
        """Convert given audio file from mp3 to wav"""
        from pydub import AudioSegment
        from pydub.playback import play
        from pydub.utils import mediainfo

        wav_file = AudioSegment.from_mp3(
            self.mp3_file).export(self.wav_file, format="wav")
        log.info('wav file generated: {}'.format(self.wav_filename))
        return wav_file

    def upload_audio_file_to_google_storage(self):
        """Uploads audio file to Google Cloud Storage and return the gs url"""
        from google.cloud import storage

        bucket_name = 'damaris-sound-bucket'
        filename = self.filename
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_filename(self.wav_file)
        url = 'gs://{0}/{1}'.format(bucket_name, filename)
        log.info('File {} uploaded to {}'.format(self.wav_file, url))
        return url

    def send_email(self):
        """Send email with transcription attached"""
        import base64
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import (Mail, Attachment, Email,
                                           FileContent, FileName,
                                           FileType)

        text_file = "transcription.txt"
        mail = Mail(
            from_email=Email('chi@damaris.com', "Chi from Damaris"),
            to_emails=self.email,
            subject="Your transcription from Damaris 🔥",
            plain_text_content="Thank you for using Damaris. Please find \
            attached your transcribed file."
        )

        with open(text_file, 'rb') as f:
            data = f.read()

        encoded_text_file = base64.b64encode(data).decode()
        attachment = Attachment()
        attachment.file_content = FileContent(encoded_text_file)
        attachment.file_type = FileType("text/plain")
        attachment.file_name = FileName("transcription.txt")
        mail.attachment = attachment

        try:
            sg = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
            sg.send(mail)
            log.info('Email sent successfully!')
        except Exception as e:
            log.error("Could not send email {}".format(e))

    def transcribe_file(self):
        """Transcribe the given audio file asynchronously"""
        client = speech.SpeechClient()
        with wave.open(self.wav_file, 'rb') as audio_file:
            content = audio_file.readframes(audio_file.getnframes())

        audio = types.RecognitionAudio(content=content)
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=44100,
            audio_channel_count=2,
            language_code='en-NG')

        log.info('Waiting for operation to complete')
        response = client.recognize(config, audio)

        if os.path.exists(self.transcription_filename):
            os.remove(self.transcription_filename)

        try:
            with open(self.transcription_filename, 'a') as file:
                for result in response.results:
                    file.write(result.alternatives[0].transcript + '\n')
        except FileNotFoundError:
            log.error('File not found')

        self.send_email()

    def transcribe_gcs(self, gcs_uri):
        """
        Asynchronously transcribes the audio file specified by the gcs_uri.
        """
        from google.cloud import speech
        from google.cloud.speech import enums
        from google.cloud.speech import types
        client = speech.SpeechClient()

        audio = types.RecognitionAudio(uri=gcs_uri)
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=44100,
            audio_channel_count=2,
            language_code='en-NG')

        log.info('Waiting for operation to complete...')

        if os.path.exists(self.transcription_filename):
            os.remove(self.transcription_filename)

        operation = client.long_running_recognize(config, audio)
        response = operation.result()
        try:
            with open(self.transcription_filename, 'a') as file:
                for result in response.results:
                    file.write(result.alternatives[0].transcript + '\n')
        except FileNotFoundError:
            log.error('File not found')

        self.send_email()


def main(filename, email):
    test = Transcribe(filename, email)
    test.start_process()
