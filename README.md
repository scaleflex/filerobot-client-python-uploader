## Filerobot Client Python Uploader

A simple Python migration script for uploading/migrating large amount of files from an existing http or ftp storage into Filerobot. This script leverages the Filerobot [POST Upload API](https://docs.filerobot.com/go/filerobot-documentation/en/store-manage/store-apis/file-apis/upload-files) with remotely hosted files fed into the script via a TXT file.

The script is running in Python 3.7 and is wrapped in Docker Compose for easy start and configuration.

## Running the script
First, clone the repository localy on the machine you want to run the migration script:
```bash
git clone https://github.com/scaleflex/filerobot-client-python-uploader.git
```

Then, browse the repository and create a copy of the sample configuration file into `.env`. You can reuse the `.env.sample` as a base for additional migrations.
```bash
cd filerobot-client-python-uploader && cp .env.sample .env
```

Read carefully all configuration options in the `.env` file and fill them accordingly. [Details at the end of this README](https://github.com/scaleflex/filerobot-client-python-uploader#configuration-options-in-env-file).

After saving the `.env` file start the Docker containers:
```bash
bash scripts/deploy-containers.sh
```

Tu run the containers in detached mode (you will not see live logs):
```bash
bash scripts/deploy-containers-detached.sh
```

If the `.env` file is correctly loaded, the following service will be running:  

![docker compose ps](/docs/static/docker-compose-ps.png)

A set of API endpoints will be available locally on the machine for you to manage your migration. You can obviously call these APIs remotely if your machine is reachable over the network.

### API endpoints to trigger
Triggering and monitoring your migration involves calling some local APIs. 

Host is `localhost` as you are running the containers locally. You can expose the server running this migration script to the Internet and call the APIs remotely as well.

```
http://localhost:8000/
Description: confirm that the container is up and rnuning
Response: {"status":"OK"}

http://localhost:8000/create-db
Description: endpoint to initiate local DB for storing the migration results (required before you run any migrations)
Response: {"status":"OK"}

http://localhost:8000/load-urls
Description: load a file and put the results into the DB, currently it should be a .TXT file with one URL to a file to upload into Filerobot per line. More infro about the function load_urls in main.py
Response: {"status":"OK"}

http://localhost:8000/run
Description: start the migration
Response: {"status":"OK"}
```

### Monitor the migration process
You can monitor the progress and results of each migration using the buil-in **pgadmin**.
Open http://localhost:5050 and enter the credetentials defined for PGADMIN_EMAIL and PGADMIN_PASS in the `.env` file.
The first time you start pgadmin, you will need to create a connection to the database.
Please refer to the sample configuration below, espetially the host, which is the docker-compose service name:

![PG admin config](/docs/static/pg-admin-config.png)

You can also attach to a specific image with the following command:
```
docker logs --follow <container_id>
```

### Check results

An easy way to check the progress and results of your migration is by running following query in pgadmin:

```sql
SELECT * FROM urls WHERE result is NOT NULL
```

Any record having `upload_started = true` and `result = NULL` represents a file that is either currently being uploaded or where the upload has failed. Reasons for failed uploads are:

- missing file at your origin (404)
- failed download from your origin because of slow network (timeout)


## Configuration options in .env file

#### Prefix of the images in Compose structure
COMPOSE_PROJECT_NAME=filerobot_uploader

#### How many concurent upload to trigger (1 to 20, depends on file size and origin speed)
WORKERS_CONCURRENCY_UPLOAD=7

#### Local DB user - you can leave default value
POSTGRES_USER=filerobot

#### DB name - you can leave default value
POSTGRES_DB=filerobot

#### Locan DB pass - you can leave default value
POSTGRES_PASS=123456

#### Admin email for PGAdmin service - adapt to your needs, no verification sent
PGADMIN_EMAIL=someone@scaleflex.com

#### Password for PGAdmin service - adapt to your needs
PGADMIN_PASS=123456

#### Your Filerobot token
FILEROBOT_TOKEN = ""

#### Your Filerobot API key (upload permisssion required)
FILEROBOT_KEY = ""

#### Target Filerobot upload folder
FILEROBOT_DIR = "/test"

Advanced configuraiton options are availalbe in `constants.py`:

#### Upload batch size: how many files should be uploaded in a single API call 

The Filerobot Uploaders will download files in batches from your origin storage over http or ftp. Reduce FILEROBOT_UPLOAD_BATCH_SIZE if you have bandwith issues at your origin that could cause failed file uploads (maximum = 100, recommended 20).

FILEROBOT_UPLOAD_BATCH_SIZE = 20

#### Max retries of Filerobot operations
FILEROBOT_MAX_RETRIES = 2

## Services
- **postgres** - DB to store uploaded file information
- **pgadmin** - service for querying the DB
- **redis** - communication between app and workers
- **app** - the main app and basic endpoints
- **worker_system** - worker for system tasks, which should be quick and simple
- **worker_upload** - worker for the heavy task with uploading files

## Roadmap
- Support CSV as list of files to be uploaded with per-file target folder and metadata
- Support Multipart upload from large local files using PUT (streaming)
- Advanced retry logic for re-uploading single failed file uploads (download from origin has failed with status code different from 404)
- Post-run statistics to help finetuning `WORKERS_CONCURRENCY_UPLOAD`, `FILEROBOT_UPLOAD_BATCH_SIZE` and `FILEROBOT_MAX_RETRIES`
- Leverage the Filerobot-CLI for atomic operations
