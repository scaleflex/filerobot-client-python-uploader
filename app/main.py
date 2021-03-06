import logging
import os
import time

import uvicorn
from fastapi import FastAPI
from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict

from app.constants import DATA_DIR
from app.tasks.celery_worker import insert_url, create_upload_batches
from app.sql import engine

log = logging.getLogger(__name__)

app = FastAPI()


def celery_on_message(body):
    """
    Logging for messages, coming from Celery
    """
    log.warning(body)


def get_results(limit):
    """
    Fetch results from DB
    """
    with engine.connect() as con:
        rs = con.execute("SELECT url FROM urls WHERE upload_started is NULL ORDER BY id DESC LIMIT {}".format(limit))
        return rs

@app.get("/")
async def read_root():
    """
    Main path of the API. Just for confirmation that all is working.
    """
    return {"status": "OK"}


@app.get("/load-urls")
async def load_urls():
    """
    Load URLS from a file in DATA_DIR, define the name of the file
    """
    with open(os.path.join(DATA_DIR, "small.txt")) as f:
        lines = f.readlines()

    # Strips the newline character
    for line in lines:
        line = line.strip()
        insert_url.apply_async(args=[line])

    return {"status": "OK"}

@app.get("/run")
async def run():
    """
    Run the actual uploading in batches
    """
    while True:
        # Define how many results to try to upload in 1 minute
        results = get_results(300)
        urls_for_parse = []
        for result in results:
            url, *_ = result
            urls_for_parse.append(url)

        create_upload_batches.apply_async(args=[urls_for_parse])
        # How many seconds to sleep
        time.sleep(60)


    return {"status": "OK"}

@app.get("/create-db")
async def create_db():
    """
    Create the DB initially, in the begining of script execution
    """
    metadata = MetaData()
    urls = Table('urls', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('url', String(1200), unique=True),
                 Column('upload_started', Boolean, default=False),
                 Column('result', String(1200), nullable=True),
                 )
    metadata.create_all(engine)
    return {"status": "OK"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

