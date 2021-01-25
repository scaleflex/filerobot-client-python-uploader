from celery import Celery

from app.constants import CELERY_BACKEND, CELERY_BROKER

celery_app = Celery(
    "worker",
    backend=CELERY_BACKEND,
    broker=CELERY_BROKER
)

celery_app.conf.task_routes = {
    "app.tasks.celery_worker.insert_url": {"queue": "system-queue"},
    "app.tasks.celery_worker.update_upload_started": {"queue": "system-queue"},
    "app.tasks.celery_worker.update_upload_response": {"queue": "system-queue"},
    "app.tasks.celery_worker.create_upload_batches": {"queue": "upload-queue"},
    "app.tasks.celery_worker.upload_files": {"queue": "upload-queue"}
}

celery_app.conf.update(task_track_started=True)
