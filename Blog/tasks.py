import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_admin_message(message):
    logger.info("[Admin] " + message)


@shared_task
def send_user_message(username, message):
    logger.info(f"[User: {username}] " + message)


@shared_task
def print_contact_message(name, email, message):
    logger.info(f'Contact Form Submission from {name}')
    logger.info(f'From: {email}\n\n{message}')
