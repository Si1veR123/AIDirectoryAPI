from django.contrib.auth.models import AbstractUser
from django.db import models
from tool.models import Domain

class CustomUser(AbstractUser):
    interested_domain = models.ForeignKey(Domain, on_delete=models.SET_NULL, null=True, blank=True)
    email_alerts = models.BooleanField(default=False)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    favourite_tools = models.ManyToManyField('tool.Tool', blank=True)