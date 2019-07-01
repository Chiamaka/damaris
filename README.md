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
- `"email:string"` The email you want the transcription to be sent to.

**Response**

- `201 Created` on success

---

## Learnings

- ~~Only Google Cloud Storage URIs are supported as the audio uri (format: gs://bucketName/object_name). This means when we get the audio from the frontend, we have to upload it to Google Cloud Storage and then get the URI then pass it to the `speech:recognize` request~~

- The above assumption is wrong. Audio content can be sent directly (if the audio is less than 1 minutes long) to the Cloud Speech-to-Text API or it can process audio content that resides in Google Cloud Storage.

- [Audio longer than ~1 minute must use the uri field to reference an audio file in Google Cloud Storage. Audio longer than ~1 minutes has to use Asynchronous Requests](https://cloud.google.com/speech-to-text/quotas)

- This is the client library for accessing the Cloud Speech-to-Text API `google-cloud-speech`

- If file size or data transmission is important to you, choose `FLAC` as your audio encoding choice.

**Checkpoint**
https://cloud.google.com/speech-to-text/docs/sync-recognize#speech-sync-recognize-python

**Todo**

1. Write a function that converts any audio format to flac
2. Write a function to upload audio that is more than 1 minute to Google Storage

### Tuesday 09/04/19

Test different audio formats with the script

- wav: wav works but I have to specify `audio_channel_count` if it has more than one audio channel
- flac: flac works. Since this is the recommended format. I should write a function that converts any audio format to flac
- m4a: took forever to run so I'm assuming it doesn't work
- mp3 is an example of lossy encoding technique and should be avoided if you have control over the media

### Wednesday 10/04/19

- Read on thoughts around converting mp3 to flac. Pros and cons

Converting from lossy compressed files (mp3) to lossless compressed files (flac) doesnt make much sense. Lossy files discard some of the original sound data and once that data is gone, there is no getting it back. So even if you convert to lossless, it's still dealing with data that is "truncated" and doesnt make a difference. Plus the lossless file would take up more space. (this is because lossless preserves all of the file's original data).

Verdict: 👎🏽
We can convert to wav instead

### Thursday 10/04/19

Sacrified yesterday to continue work on workbox, offline access in Chicken Sandwich

### Friday 11/04/19

https://towardsdatascience.com/how-to-use-google-speech-to-text-api-to-transcribe-long-audio-files-1c886f4eb3e9

- ~~Write a function to convert from mp3 to wav~~
- ~~Consolidate the script~~

**Todo**

Steps to finalizing the transcribe function

1. ~~Get the mp3 file~~
2. ~~Convert to wav~~
3. ~~Upload the converted file to Google Cloud Storage~~
4. ~~Construct the GS url and pass to the transcribe_gcs function~~
5. Create a word document with the transcription
6. Write the code as a class
7. Write a service to send an email when the transcription is complete

**Bug**
When I run the transcribe_audio function, I get an error that says "No such file or directory: 'ffprobe': 'ffprobe'"

Warn: Couldnt find ffprobe or avprobe - defaulting to ffprobe but may not work

I feel like it has something to do with some utils missing in the pydub version I have installed in docker

I can try downgrading.

## Monday 13/05/19

It works now 🤷🏽‍♀️

I want kind of like a two-prong approach:

If the length/duration is greater than one minute, upload to google storage, return the `gsuri` and process.

If the length is less than one minute, process immediately (no need uploading to google storage)

## Tuesday 14/05/19

Think about how to remove the hardcoded storage values. They kinda suck :(

Thoughts:
I can get the file name from the frontend. That would eliminate having to hardcode the name used to upload the files to my storage bucket.

## Wednesday 15/05/19

- ~~Configure sendgrid API and send a test email to myself :D~~

## Thursday and Friday 16-17/05/19:

- ~~Send attachments with email :D~~

## Monday 20/05/19:

- Had a problem sending emails. In the email activity on sendgrid, it says the email has been delivered but I dont see it in my email. I tried verifying my domain on sendgrid but I think it would take sometime before the records are consolidated so I'll try again tomorrow.

## Tuesday 21/05/19:

- The emails were in spam. **Remember to add it to the instructions on the site; if you dont see your email, please check spam and check it as not spam so it can come in directly another time.**

## Wednesday 22/05/19:

- The server was very freaking annoying. No idea what was up with it. I spent my full 40 mins and shut down my machine

## Thursday 23/05/19:

- I figured out how to accept and save audio files :D. I'm really really happy. I also added validations in case of wrong extension types being uploaded (I'll also do this on the frontend). Also return sensible error messages when things dont go according to plan. All in all, I'm really happy with my progress today.

## Friday 24/05/19:

- ~~Validate email~~
- ~~Sensible error messages for the frontend~~
- ~~Pass email and audio to transcribe~~

## Monday - Tuesday 28/05/19:

- Succesfully added the email and filename to the class and also found a simple hack for consistency for the audio uploads
- started refactoring the code class. knocked off the `convert_from_mp3_to_wav` method; thoroughly tested

## Wednesday - Thursday 30/05/19:

- I'm done refactoring the code. It is fully class based and no longer using constants for the wav_filename and the transcription name.

## Todo

- ~~Implement logger~~

---

# Improvements

- Remove the transcribe function from the request lifecycle by using a background runner/task queue so that requests don't timeout

1. Add Celery
2. Send an async request to celery

- Change from sendgrid to flask-mail

https://dabble-of-devops.com/deploy-a-celery-job-queue-with-docker-part-1/
