from datetime import timedelta
from django.conf import settings
from django.utils import timezone

def set_due_date():
    return timezone.now().date() + timedelta(days=settings.LOAN_DAYS)