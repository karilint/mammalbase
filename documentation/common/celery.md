# Celery and Celery Beat

This project supports running tasks in the background, implemented with the Celery module. The proper version of the 
documentation can be found [here](https://docs.celeryq.dev/en/v5.2.7/). This project also supports 
running periodic tasks in Celery using Celery Beat, a scheduler built in Celery. 

## Running Tasks With Celery

Celery tasks can be defined as functions in a file named `tasks.py`, located inside an app directory. The function must
be decorated with `@shared_task` in order to be discovered by the Celery app. To run a shared task named `some_task` in 
the background it can be called with either `some_task.delay()` or `some_task.apply_async()` methods. The `delay` is 
probably easier to use as you can give arguments to it in a normal manner, but in case one needs more control over
the task `apply_async` might be a better solution. 

## Running Periodic Tasks With Celery Beat

Running tasks with Celery Beat is also pretty straightforward. Create a Celery task to some `tasks.py` file and define
a periodic task in the Django settings file `app/config/setting.py`. All periodic tasks are defined in a single 
dictionary stored in a variable called `CELERY_BEAT_SCHEDULE`. The documentations of the available fields can be found 
[here](https://docs.celeryq.dev/en/v5.2.7/userguide/periodic-tasks.html#available-fields) and can be in the simplest
form something like
```
"name-for-your-task": {
    "task": "module.tasks.some_task",
    "schedule": timedelta(minutes=1),
    "args":(),
    "options": {
    }
}
```
This configuration runs `some_task` every minute as long as it is not stopped.
