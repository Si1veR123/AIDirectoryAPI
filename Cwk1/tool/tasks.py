from django.core.mail import send_mail
from user.models import CustomUser
from django.tasks import task
from django.conf import settings

@task
def send_domain_email(tool_name, domain, url):
    users = CustomUser.objects.filter(interested_domain__name=domain, email_alerts=True)
    emails = [user.email for user in users if user.email]

    send_mail(
        subject="New tool in your interested domain",
        message=f"{tool_name} is a new tool in your interested domain {domain}. Check it out at {url}!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=emails
    )