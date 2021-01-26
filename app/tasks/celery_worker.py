import logging
import os

from app.constants import FILEROBOT_UPLOAD_BATCH_SIZE, FILEROBOT_MAX_RETRIES
from app.filerobot import Filerobot
from .celery_app import celery_app
from app.sql import engine

log = logging.getLogger(__name__)


@celery_app.task()
def insert_url(url):
    try:
        with engine.connect() as con:
            rs = con.execute("INSERT INTO urls(url) VALUES('{}')".format(url))
    except:
        log.warning(f"ERROR insert_url for {url}")


@celery_app.task()
def extract_info(input_file, target_dir):
    pass


@celery_app.task()
def create_upload_batches(url_list):
    print(f"FILE LIST - {url_list}")
    # Creating batches for upload to Filerobot
    for x in range(0, len(url_list), FILEROBOT_UPLOAD_BATCH_SIZE):
        partial_list = url_list[x:x + FILEROBOT_UPLOAD_BATCH_SIZE]
        upload_files.apply_async(args=[partial_list])
        update_upload_started.apply_async(args=[partial_list])


@celery_app.task()
def update_upload_started(url_list):
    print(f"update_upload_started -- {url_list}")
    with engine.connect() as con:
        for url in url_list:
            rs = con.execute("UPDATE urls SET upload_started = TRUE WHERE url = '{}'".format(url))

@celery_app.task()
def update_upload_response(url, result):
    print(f"update_upload_response for {url} -- {result}")
    with engine.connect() as con:
        rs = con.execute("UPDATE urls SET result = '{}' WHERE url = '{}'".format(result, url))

@celery_app.task()
def upload_files(url_list, executions=1):
    filerobot_token = os.environ.get("FILEROBOT_TOKEN")
    filerobot_key = os.environ.get("FILEROBOT_KEY")

    if None in (filerobot_key, filerobot_token):
        print("No Filerobot Credetentials")

    # Initialize the Filerobot instance with
    filerobot = Filerobot(
        filerobot_token=filerobot_token,
        filerobot_key=filerobot_key,
    )

    response, result_json = filerobot.urls_upload(url_list)

    if response.status_code == 200:
        file_data = result_json.get("files", None)
        if file_data is not None:
            for file in file_data:
                url = file.get("info", {}).get("origin")
                result = file.get("url", {}).get("permalink")
                update_upload_response.apply_async(args=[url, result])
        else:
            file_data = result_json.get("file")
            url = file_data.get("info", {}).get("origin")
            result = file_data.get("url", {}).get("permalink")
            update_upload_response.apply_async(args=[url, result])

        return result_json
    else:
        print(result_json)
        # If we tried already a lot of times to upload without good result, stop the operation now
        if executions > FILEROBOT_MAX_RETRIES:
            log.warning(f"FILEROBOT_MAX_RETRIES {FILEROBOT_MAX_RETRIES} reached")
            raise Exception

        # Retry the upload in step of 10 seconds for each execution (1->5, 2->10, 3->15, etc.)
        upload_files.apply_async(args=[url_list, executions + 1], countdown=executions * 5)
