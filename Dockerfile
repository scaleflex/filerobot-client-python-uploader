FROM python:3.7-alpine

# ENV variables
ENV DOCKER=true

# Install Docker dependencies for PostgreSQL
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# Expose a port
EXPOSE 80

# Copy the current app to Docker container
COPY ./app /app

# Install dependencies
RUN pip install -r /app/requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
