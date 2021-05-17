from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(TeacherProfile)
admin.site.register(StudentProfile)
admin.site.register(Room)
admin.site.register(Discipline)
admin.site.register(Homework)



