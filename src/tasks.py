import os
from celery import Celery


def make_celery(app):
    celery = Celery(app.import_name,
                    backend=os.environ.get('CELERY_RESULT_BACKEND'),
                    broker=os.environ.get('CELERY_BROKER_URL'))
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
