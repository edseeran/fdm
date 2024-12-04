from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from apps.UserAccount.serializers import LoginSerializer

class LoginAPIView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            session_id = request.session.session_key
            csrf_token = get_token(request)
            response_data = {'detail': 'User is already logged in', 'session_id': session_id, 'csrf_token': csrf_token}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            session_id = request.session.session_key
            csrf_token = get_token(request)
            response_data = {'detail': 'Login successful', 'session_id': session_id, 'csrf_token': csrf_token}
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CheckLoggedInAPIView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            user_id = request.user.id
            data = {'user_id': user_id}
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {'User is not logged in'}
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

class LogoutAPIView(APIView):
    def post(self, request):
        logout(request)
        csrf_token = get_token(request)
        response_data = {'detail': 'Logout successful', 'csrf_token': csrf_token}
        return Response(response_data, status=status.HTTP_200_OK)
