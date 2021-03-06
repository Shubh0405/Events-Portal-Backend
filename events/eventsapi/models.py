from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import MaxValueValidator, MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField

class UserManager(BaseUserManager):
    def create_user(self, username, email, phone_number, password=None):
        if username is None:
            raise TypeError('Users should have a username')
        if email is None:
            raise TypeError('Users should have a Email')

        user = self.model(username=username, email=self.normalize_email(email), phone_number=phone_number)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password):
        if password is None:
            raise TypeError('Password should not be none')
        phone_number = '1234567890'
        user = self.create_user(username, email, phone_number, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    phone_number = PhoneNumberField()
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    otp = models.IntegerField(blank=True,null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.username

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return{
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }

class Event(models.Model):
    name = models.CharField(max_length=255,unique=True)
    registered_users = models.ManyToManyField(User,through="Event_Registration")

    def __str__(self):
        return self.name

class Event_Registration(models.Model):
    event = models.ForeignKey(Event,related_name="event_registration",on_delete=models.CASCADE)
    user = models.ForeignKey(User,related_name="user_events",on_delete=models.CASCADE)

    class Meta:
        unique_together = ('event','user')

    def __str__(self):
        return self.user.username + ' Registered in ' + self.event.name

class Feedback(models.Model):
    event = models.ForeignKey(Event,related_name="event_feedback",on_delete=models.CASCADE)
    user = models.ForeignKey(User,related_name="user_event_feedback",on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return self.event.name + ' By ' +self.user.username
