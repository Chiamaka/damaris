# Damaris Backend

## Usage

## Endpoints

### Transcribe audio to text

**Definitions**

`POST /transcribe-audio`

**Description**
Send audio data to the Speech-to-Text Google API which then returns a text transcription of that audio file.
So the frontend posts the audio file to the backend (which is this API) and the backend gets the audio file, then send it to the Speech-to-Text API and that processes the audio and returns the text transcription which we return to the frontend as a response

**Arguments**

- `"audio-file":blob` The audio file you would like to transcribe to text. Must be .mp3
- `"email:string"` The email you want the transcription to be sent to once transcription completes.

**Response**

- `201 Created` on success

---

## Instructions

1. Clone project: `git clone https://github.com/Chiamaka/damaris.git`
2. Go to the [Google Cloud Speech-to-Text API](https://cloud.google.com/speech-to-text/) and create a project. Download the google application credentials (this enables Google authenticate your project).
3. Create an `.env` file in the root of your application and add the `GOOGLE_APPLICATION_CREDENTIALS` url and your `SENDGRID_API_KEY`.
4. Run application with `docker-compose up --build`
5. Use your favourite client (postman) to visit the api url.
