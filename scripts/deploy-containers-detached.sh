#!/bin/bash

# Docker Compose command to build all services with force recreate
docker-compose up -d --build --force-recreate --remove-orphans