import os

# Path of this script, in Docker environment: /app/constants.py
CONTSTANTS = os.path.realpath(__file__)

# Path of the main app directory, in Docker environment: /app
APP_DIR = os.path.dirname(CONTSTANTS)

# Path of the folder, where we are making the IO operations for files
# In Docker environment: /app/data
DATA_DIR = os.path.join(APP_DIR, "data")

# Default Celery Backend and Broker to transfer tasks and information
CELERY_BACKEND = "redis://localhost:6379/0"
CELERY_BROKER = "redis://localhost:6379/1"

# If we use Docker - we have different addresses of brockers and backend
if bool(os.getenv("DOCKER")):
    # We use directly the docker-compose service of redis
    CELERY_BACKEND = "redis://redis:6379/0"
    CELERY_BROKER = "redis://redis:6379/1"

# Main endpoint to the Filerobot API. Additional method are defined in fuctions
FILEROBOT_API_ENDPOINT = "https://api.filerobot.com"

# Filerobot default directory, where to store the transcoded files
# Need to be a top level directory
FILEROBOT_UPLOAD_DIR = "/test-21-01-2021"

# Batches count, how many paths we are trying to send in a single call
FILEROBOT_UPLOAD_BATCH_SIZE = 20

# Max retries of Filerobot operations, like upload.
# How many times we will try to upload list with files, before cancel the function
FILEROBOT_MAX_RETRIES = 2

# Timeout to assing to get/post calls for the different APIs
APIS_TIMEOUT = 3000
