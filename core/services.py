"""
Core Services
=============
Handles sending out emails and creating in-app notifications.
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Notification

class EmailNotificationService:
    @staticmethod
    def send_and_create_notification(user, title, message, level='info', link='', email_subject=None, email_template_name=None, context=None):
        """
        Creates an in-app notification and optionally sends an email if configuration is provided.
        """
        # 1. Create In-App Notification
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            level=level,
            link=link
        )

        # 2. Send Email if required
        if email_subject and user.email:
            try:
                if email_template_name and context:
                    # Using an HTML template for email
                    html_message = render_to_string(email_template_name, context)
                    plain_message = message # fallback
                    send_mail(
                        subject=email_subject,
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True,
                        html_message=html_message
                    )
                else:
                    # Plain text email
                    send_mail(
                        subject=email_subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True
                    )
            except Exception as e:
                # Log email failure (in production use proper logging)
                print(f"Failed to send email to {user.email}: {e}")
