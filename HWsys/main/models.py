from django.db import models
from datetime import date, datetime, timedelta

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255, unique=True)

    email = models.EmailField(db_index=True, unique=True)

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    # Свойство USERNAME_FIELD сообщает нам, какое поле мы будем использовать
    # для входа в систему. В данном случае мы хотим использовать почту.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Сообщает Django, что определенный выше класс UserManager
    # должен управлять объектами этого типа.
    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def token(self):
        """
        Позволяет получить токен пользователя путем вызова user.token, вместо
        user._generate_jwt_token(). Декоратор @property выше делает это
        возможным. token называется "динамическим свойством".
        """
        return self._generate_jwt_token()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def get_email(self):
        return self.email

    def _generate_jwt_token(self):
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор этого
        пользователя, срок действия токена составляет 1 день от создания
        """
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')


class Discipline(models.Model):
    discipline_type = models.TextField(default='')

    def __str__(self):
        return self.discipline_type


class TeacherProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Discipline, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "User: {}".format(self.user)


class StudentProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bd = models.DateField("Birthday", default=datetime.now)

    def __str__(self):
        return "User: {}".format(self.user)


class Room(models.Model):
    lesson = models.ForeignKey(Discipline, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.now)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)

    def __str__(self):
        return "lesson: {}, created at: {}, teacher: {}".format(self.lesson, self.created_at, self.teacher)


class Homework(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, default=1)
    lesson = models.ForeignKey(Discipline, on_delete=models.CASCADE, blank=True, null=True)
    date_published = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(default=None)
    is_finished = models.BooleanField(default=False)
    file = models.FileField(upload_to='homeworks/')

    def __str__(self):
        return "lesson: {}, created at: {}, teacher: {}".format(self.lesson, self.date_published, self.teacher)
