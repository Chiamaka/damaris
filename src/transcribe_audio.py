import wave
import os
import re

from google.cloud import speech
from google.cloud import storage
from google.cloud.speech import enums
from google.cloud.speech import types
from pydub import AudioSegment
from . import constants
from .email_client import send_email
from .logger import logger

log = logger()


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
        import wave
        with wave.open(self.wav_file, 'r') as frame:
            frames = frame.getnframes()
            rate = frame.getframerate()
            duration = frames / float(rate)
            return duration

    def convert_from_mp3_to_wav(self):
        """Convert given audio file from mp3 to wav"""
        wav_file = AudioSegment.from_mp3(
            self.mp3_file).export(self.wav_file, format="wav")
        log.info('wav file generated: {}'.format(self.wav_filename))
        return wav_file

    def upload_audio_file_to_google_storage(self):
        """Uploads audio file to Google Cloud Storage and return the gs url"""
        bucket_name = 'damaris-sound-bucket'
        filename = self.filename
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_filename(self.wav_file)
        url = 'gs://{0}/{1}'.format(bucket_name, filename)
        log.info('File {} uploaded to {}'.format(self.wav_file, url))
        return url

    def transcribe_file(self):
        """Transcribe the local audio file"""
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

        send_email(self.email, self.transcription_filename)

    def transcribe_gcs(self, gcs_uri):
        """
        Asynchronously transcribes the audio file specified by the gcs_uri.
        """
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

        send_email(self.email, self.transcription_filename)


def main(filename, email):
    test = Transcribe(filename, email)
    test.start_process()
