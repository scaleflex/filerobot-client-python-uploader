## Filerobot Client Python Uploader

A simple Python migration script for uploading large amount of files into Filerobot

The script is running in Python 3.7 and it is wrapped in Docker Compose for easy start and configuration.

## Running
```bash
bash scripts/deploy-containers.sh
```

## Services
- **postgres** - DB to store information about files.
- **pgadmin** - service for inspecting the DB.
- **redis** - communication between app and workers.
- **app** - the main app and basic endpoints.
- **worker_system** - worker for system tasks, which should be quick and simple.
- **worker_upload** - worker for the heavy task with uploading files.

## Configuration
TO DO
