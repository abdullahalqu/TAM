"""
Redis Queue setup
"""
import os
from redis import Redis
from rq import Queue
from app.logging_config import get_logger

logger = get_logger(__name__)

# Connect to Redis
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_conn = Redis.from_url(redis_url)

# Create queue
task_queue = Queue('tasks', connection=redis_conn)


def enqueue_notification(task_id: str, task_title: str, user_email: str, action: str):
    """
    Enqueue a notification task to be processed by RQ worker
    """
    from app.workers.tasks import send_task_notification

    logger.info(
        f"Enqueuing notification job: {action}",
        extra={
            "queue_name": "tasks",
            "job_type": "send_task_notification",
            "task_id": task_id,
            "task_title": task_title,
            "user_email": user_email,
            "action": action,
            "queue_status": "enqueuing"
        }
    )

    job = task_queue.enqueue(
        send_task_notification,
        task_id=task_id,
        task_title=task_title,
        user_email=user_email,
        action=action,
        job_timeout='5m'  # Job timeout
    )

    logger.info(
        f"Notification job enqueued successfully: {action}",
        extra={
            "queue_name": "tasks",
            "job_type": "send_task_notification",
            "job_id": job.id,
            "task_id": task_id,
            "action": action,
            "queue_status": "enqueued",
            "queue_position": len(task_queue)
        }
    )

    return job.id
