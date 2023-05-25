from celery import shared_task


@shared_task
def hello_world_celery():
    print('Hello from the Celery world!')
