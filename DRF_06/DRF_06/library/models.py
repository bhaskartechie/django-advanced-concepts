from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    publication_year = models.PositiveIntegerField()

    def __str__(self):
        return self.title


# Custom user manager
class CustomUserManager(BaseUserManager):
    def create_user(self, userid, firstname, email, gender, notified=False):
        if not userid:
            raise ValueError('Users must have a userid')
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            userid=userid,
            firstname=firstname,
            email=self.normalize_email(email),
            gender=gender,
            notified=notified,
        )
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, userid, firstname, email, gender, notified=False, password=None):
        user = self.create_user(
            userid=userid,
            firstname=firstname,
            email=email,
            gender=gender,
            notified=notified,
        )
        user.is_staff = True
        user.is_superuser = True
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    userid = models.CharField(max_length=8, unique=True)
    firstname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10)
    notified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'userid'
    REQUIRED_FIELDS = ['firstname', 'email', 'gender']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.firstname} ({self.userid})"
