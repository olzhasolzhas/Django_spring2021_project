from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from .serializers import *
from .forms import *

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied

from django.core.files.storage import FileSystemStorage
from django.views.generic import ListView, CreateView
from django.http import JsonResponse


def index(request):
    return render(request, 'index.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register/register.html', {
        'form': form
    })


class RegistrationAPIView(APIView):
    """
    Разрешить всем пользователям (аутентифицированным и нет) доступ к данному эндпоинту.
    """
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Паттерн создания сериализатора, валидации и сохранения - довольно
        # стандартный, и его можно часто увидеть в реальных проектах.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Обратите внимание, что мы не вызываем метод save() сериализатора, как
        # делали это для регистрации. Дело в том, что в данном случае нам
        # нечего сохранять. Вместо этого, метод validate() делает все нужное.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class Logout(APIView):
    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class IsStudent(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsTeacher(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class TeacherList(APIView):
    def get(self, request):
        teacher = TeacherProfile.objects.all()
        serializer = TeacherProfileSerializer(teacher, many=True)
        return Response(serializer.data)


class TeacherDetailsView(APIView):
    def get(self, request, pk):
        teacher = TeacherProfile.objects.get(id=pk)
        serializer = TeacherProfileSerializer(teacher)
        return Response(serializer.data)

# ------------------------------------------------


class StudentView(generics.ListAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer


class StudentUpdateView(generics.UpdateAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = CreateStudentProfileSerializer
    permission_class = permissions.IsAuthenticatedOrReadOnly
    permission_classes = (IsStudent,)


class StudentCreateView(generics.CreateAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = CreateStudentProfileSerializer
    permission_classes = (IsStudent,)


class StudentDeleteView(generics.DestroyAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = (IsStudent,)


# -------------------------------------------------


class HomeworkListView(ListView):
    model = Homework
    template_name = 'hws.html'


def hw_list(request):
    hws = Homework.objects.all()
    return render(request, 'hws.html', {
        'hws': hws
    })


def upload(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['url'] = fs.url(name)
    return render(request, 'upload.html', context)


def upload_hw(request):
    if request.method == 'POST':
        form = HwForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('hw_list')
    else:
        form = HwForm()
    return render(request, 'upload_hw.html', {
        'form': form
    })


class UploadHwView(CreateView):
    model = Homework
    form_class = HwForm
    success_url = reverse_lazy('hw_list')
    template_name = 'upload_hw.html'
    permission_classes = (IsTeacher,)


class ProfileReview(ListView):
    def get(self, request):
        if IsTeacher:
            teacher = TeacherProfile.objects.all()
            serializer = TeacherProfileSerializer(teacher, many=True)
            return Response(serializer.data)
        if IsStudent:
            student = StudentProfile.objects.all()
            serializer = StudentProfileSerializer(student, many=True)
            return Response(serializer.data)
    template_name = 'profile.html'
