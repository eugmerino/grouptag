from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import UserProfileView
from .serializers import MyTokenObtainPairSerializer

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view(serializer_class=MyTokenObtainPairSerializer), name='token_obtain_pair'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
]