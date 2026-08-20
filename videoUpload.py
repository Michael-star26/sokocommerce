import apivideo
from app import videoMedia
from apivideo.api.videos_api import VideosApi
import os
from apivideo.api import *
from flask import *

api_key="ya1rNwl5y4pT76NRhvWakFvm0er9Z23AdiW4sQva3c9"
def uploads():
    with apivideo.AuthenticatedApiClient(api_key) as client:
        # Set up to use the videos endpoint
        videos_api=VideosApi(client)
        client.connect()

        app = Flask(__name__)
        app.config['MAX_CONTENT_LENGTH'] = 5000 * 5000 * 100000
        app.config['UPLOAD_EXTENSIONS'] = ['.mov', '.mp4', '.m4v', '.jpm', '.jp2', '.3gp', '.3g2', '.mkv', '.mpg',
                                           '.ogv',
                                           '.webm', '.wmv']
        app.config['UPLOAD_PATH'] = './static/files/videos'
        # Add the file name from the FileStorage object from Flask
        video_create_payload = {
            "title": uploaded_file.filename,
        }
        # Create a video container to upload your video into and retrieve the video ID for the container
        response = videos_api.create(video_create_payload)
        video_id = response["video_id"]
        # Upload your file as a stream. NOTE! IMPORTANT! If you are uploading a big file, this will take awhile if it's over 128MB.
        video_response = videos_api.upload(video_id, uploaded_file.stream)

