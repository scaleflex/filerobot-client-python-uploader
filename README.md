## Filerobot Client Python Uploader

A simple Python migration script for uploading large amount of files into Filerobot

The script is running in Python 3.7 and it is wrapped in Docker Compose for easy start and configuration.

## Running the script
First you need to clone the repository localy:
```bash
git clone https://github.com/scaleflex/filerobot-client-python-uploader.git
```

Enter the repository and add copy the sample configuration file (as the script need .env file to work)
```bash
cd filerobot-client-python-uploader && cp .env.sample .env
```

Read carefully all the configuration in the .env file and fill them accordingly. There are commments to each one, describing the exact behaviour.

When ready, you need to start the containers:
```bash
bash scripts/deploy-containers.sh
```

If you want to be in detached mode (you will not see live logs):
```bash
bash scripts/deploy-containers-detached.sh
```

If everything is correct, you need to see the following service running:  
![docker compose ps](/docs/static/docker-compose-ps.png)

### Endpoints to trigger
It is basically a simple API with some operations, which help to upload files. There are endpoints, which triggers different operation.
Host is **localhost** as you are running the containers locally.
```
http://localhost:8000/
Description: Just to confirm container is UP
Response: {"status":"OK"}

http://localhost:8000/create-db
Description: Trigger this endpoint the first time, creating the DB to store the results
Response: {"status":"OK"}

http://localhost:8000/load-urls
Description: Load a file and put the results into the DB, currently it should be a .TXT file with URLS in a single line. Check the function load_urls in main.py.
Response: {"status":"OK"}

http://localhost:8000/run
Description: Actual running of upload operations, monitor the DB
Response: {"status":"OK"}
```

### Monitoring
You can monitor the progress and results, using the buil-in service **pgadmin**.
Open **http://localhost:5050** and enter the credetentials defined for PGADMIN_EMAIL and PGADMIN_PASS in .env file.
The first time, you need to create a connection to the service, in order to view the table.
Please refer to this configuration (espetially the host, which is the docker-compose service name):  
![PG admin config](/docs/static/pg-admin-config.png)

You can also atach to a specific image with the following command:
```
docker logs --follow <container_id>
```

### Check results
```sql
SELECT * FROM urls WHERE result is NOT NULL
```

## Configuration in .env file
Most of the configurations are placed in the .env file.
Here is a list:  
#### Prefix of the images in Compose structure
COMPOSE_PROJECT_NAME=filerobot_uploader

#### How many concurent upload to trigger (1 to 20, depends on file size and origin speed)
WORKERS_CONCURRENCY_UPLOAD=7

#### Local DB user, generally - leave like this
POSTGRES_USER=filerobot

#### DB name, generally - leave like this
POSTGRES_DB=filerobot

#### Locan DB pass, generally - leave like this
POSTGRES_PASS=123456

#### Admin email for PGAdmin service, adapt to your needs, no verification sended
PGADMIN_EMAIL=someone@scaleflex.com

#### Password for PGAdmin service, adapt to your needs
PGADMIN_PASS=123456

#### Your filerobot token
FILEROBOT_TOKEN = ""

#### Your filerobot key with upload permisssions
FILEROBOT_KEY = ""

#### Your filerobot upload dir
FILEROBOT_DIR = "/test"

There are some additionals configs, which can be controlled in constants.py. They should be changed more rarely.
A list can be find below:  
### Batches count, how many paths we are trying to send in a single call
FILEROBOT_UPLOAD_BATCH_SIZE = 20

#### Max retries of Filerobot operations, like upload.
FILEROBOT_MAX_RETRIES = 2

## Services
- **postgres** - DB to store information about files.
- **pgadmin** - service for inspecting the DB.
- **redis** - communication between app and workers.
- **app** - the main app and basic endpoints.
- **worker_system** - worker for system tasks, which should be quick and simple.
- **worker_upload** - worker for the heavy task with uploading files.


