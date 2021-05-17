from django.urls import path, re_path, include
from .views import *
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.views import TokenObtainSlidingView, TokenRefreshSlidingView

urlpatterns = [
    path('', index, name='home'),
    path('auth/token', obtain_auth_token, name='token'),
    path('register/', signup, name='register'),
    path('new_reg/', RegistrationAPIView.as_view(), name='new_reg'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("teacher/", TeacherList.as_view()),
    path('teacherDetails/<int:pk>/', TeacherDetailsView.as_view()),
    path('student/', StudentView.as_view()),
    path('student/update', StudentUpdateView.as_view()),
    path('student/create', StudentCreateView.as_view()),
    path('student/delete', StudentDeleteView.as_view()),
    path('hw/', hw_list, name='hw_list'),
    path('hw/upload/', upload_hw, name='upload_hw'),
    path('hw/upload_view/', UploadHwView.as_view(), name='upload_hw_view'),
    path('profile/', ProfileReview.as_view(), name='profile')
]