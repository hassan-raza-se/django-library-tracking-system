import logging
from celery import shared_task
from .models import Loan
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

logger = logging.Logger(__name__)

@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass


@shared_task
def check_overdue_loans():
    overdue_loans = Loan.objects.filter(
        is_returned=False, due_date__lt=timezone.now().date()
    ).select_related('member__user', 'book')
    for loan in overdue_loans:
        user_email = loan.member.user.email
        book_title = loan.book.title
        try:
            logger.info(f'sending loan overdue email to {user_email}')
            send_mail(
            subject='Book Loan overdue',
            message=f'Hello {loan.member.user.username},\n\nYou have loaned "{book_title}".\nPlease return because due date has passed',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
            )
        except:
            logger.error(f'Error sending email to user')