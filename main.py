#!/usr/bin/python

import httplib2
import os
import random
import sys
import time
import editVideo
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError,)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                   scope=YOUTUBE_UPLOAD_SCOPE,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))


def initialize_upload(youtube, options):
    tags = None
    if options.keywords:
        tags = options.keywords.split(",")

    body = dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=tags,
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacyStatus
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)


# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print("Video id '%s' was successfully uploaded." % response['id'])
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError:
            if HttpError.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (HttpError.resp.status,
                                                                     HttpError.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS:
            error = "A retriable error occurred: %s" % RETRIABLE_EXCEPTIONS

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)


#  everything else above is sample code from Google, that basically deals with the upload process and error checks to
#  a satisfactory manner. Below is where you would change the parameters of your upload, including title of video,
#  description, etc:
#  Please note, without these parameters filled out, errors are more capable of occurring
if __name__ == '__main__':
    editVideo.edit_video()
    time.sleep(1)  # make sure the video is finished before attempting to upload to YouTube
    # this is retrieved from the final path created by the editing file
    filepath = 'C:\\Users\\Remag_OW\\PycharmProjects\\YoutubeUploadBot\\edited_video.mp4'
    date = date.today() - timedelta(days=1)  # gives you the day from which the clips were from
    yesterday = date.strftime("%b-%d-%Y")

    game = twitchClips.game_name
    title = f'{yesterday} Highlights | {game}'
    desc = f'{game} highlights for {yesterday}'
    keywords = f'{game}, Gaming, Epic'

    argparser.add_argument("--file", help="Video file to upload", default=filepath)
    argparser.add_argument("--title", help="Video title", default=title)
    argparser.add_argument("--description", help="Video description",
                           default=desc)
    argparser.add_argument("--category", default="22",
                           help="Numeric video category. " + "See https://developers.google.com/youtube/v3/docs"
                                                       "/videoCategories/list")
    argparser.add_argument("--keywords", help="Video keywords, comma separated",
                           default=keywords)
    argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
                           default=VALID_PRIVACY_STATUSES[0], help="Video privacy status.")
    args = argparser.parse_args()
    # print(args)
    print()  # newline

    if not os.path.exists(args.file):
        exit("Please specify a valid file using the --file= parameter.")
    youtube = get_authenticated_service(args)
    try:
        initialize_upload(youtube, args)
        # time.sleep(.5)
        # if os.path.exists('tmp\\'):
        #     os.remove('tmp\\')
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
