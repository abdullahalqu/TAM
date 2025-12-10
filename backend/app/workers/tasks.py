"""
RQ Worker Tasks - Background job processing
"""

import time
from datetime import datetime
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.logging_config import get_logger
from rq import get_current_job

logger = get_logger("worker")


def send_task_notification(task_id: str, task_title: str, user_email: str, action: str):
    """
    Simulate sending a task notification email
    In production, this would integrate with an email service (SendGrid, AWS SES, etc.)

    Args:
        task_id: UUID of the task
        task_title: Title of the task
        user_email: Email of the user to notify
        action: Action performed (created, updated, deleted, completed)
    """
    start_time = time.time()

    # Get current RQ job context
    current_job = get_current_job()
    job_id = current_job.id if current_job else "unknown"

    logger.info(
        f"[QUEUE] Worker picked up notification job: {action}",
        extra={
            "queue_name": "tasks",
            "job_type": "send_task_notification",
            "job_id": job_id,
            "task_id": task_id,
            "task_title": task_title,
            "action": action,
            "user_email": user_email,
            "queue_status": "processing",
        },
    )

    # Simulate email sending delay
    time.sleep(2)

    duration_ms = (time.time() - start_time) * 1000

    logger.info(
        f"[QUEUE] Notification job completed: {action} - {task_title}",
        extra={
            "queue_name": "tasks",
            "job_type": "send_task_notification",
            "job_id": job_id,
            "task_id": task_id,
            "action": action,
            "user_email": user_email,
            "duration_ms": round(duration_ms, 2),
            "queue_status": "completed",
            "result": "success",
        },
    )

    return {
        "status": "sent",
        "task_id": task_id,
        "user_email": user_email,
        "action": action,
        "sent_at": datetime.utcnow().isoformat(),
        "duration_ms": round(duration_ms, 2),
    }


def process_bulk_tasks(task_ids: list):
    """
    Example of processing multiple tasks in background
    Useful for bulk operations, exports, etc.
    """
    start_time = time.time()

    # Get current RQ job context
    current_job = get_current_job()
    job_id = current_job.id if current_job else "unknown"

    logger.info(
        f"[QUEUE] Worker picked up bulk processing job",
        extra={
            "queue_name": "tasks",
            "job_type": "process_bulk_tasks",
            "job_id": job_id,
            "task_count": len(task_ids),
            "queue_status": "processing",
        },
    )

    processed = 0
    for task_id in task_ids:
        logger.info(
            f"[QUEUE] Processing bulk task {processed + 1}/{len(task_ids)}",
            extra={
                "queue_name": "tasks",
                "job_type": "process_bulk_tasks",
                "job_id": job_id,
                "task_id": task_id,
                "progress": f"{processed + 1}/{len(task_ids)}",
            },
        )
        time.sleep(0.5)
        processed += 1

    duration_ms = (time.time() - start_time) * 1000

    logger.info(
        f"[QUEUE] Bulk processing job completed",
        extra={
            "queue_name": "tasks",
            "job_type": "process_bulk_tasks",
            "job_id": job_id,
            "task_count": len(task_ids),
            "processed_count": processed,
            "duration_ms": round(duration_ms, 2),
            "queue_status": "completed",
            "result": "success",
        },
    )

    return {
        "status": "completed",
        "processed_count": processed,
        "duration_ms": round(duration_ms, 2),
    }
