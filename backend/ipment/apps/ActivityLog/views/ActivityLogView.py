from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.ActivityLog.models import ActivityLog, LoginActivity
from apps.ActivityLog.serializers import ActivityLogSerializer, ListActivityLogSerializer, LoginActivitySerializer

# @csrf_exempt
@login_required
@permission_classes([IsAuthenticated])
def activityLogApi(request, method=None, id=None):
    if method not in ['list-auth', 'list-act', 'view-auth', 'view-act']:
        return HttpResponseBadRequest("Invalid request method.")

    # Permission check for list and view methods
    if method in ['list-auth', 'view-auth'] and not request.user.has_perm('ActivityLog.view_loginactivity'):
        return JsonResponse("Permission denied.", status=403, safe=False)
    if method in ['list-act', 'view-act'] and not request.user.has_perm('ActivityLog.view_activitylog'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'list-auth':
        if request.method == 'GET':
            loginActivity = LoginActivity.objects.all()
            loginActivitySerializer = LoginActivitySerializer(activityLog, many=True)
            return JsonResponse(loginActivitySerializer.data, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'list'. Use GET.")
        
    elif method == 'list-act':
        if request.method == 'GET':
            activityLog = ActivityLog.objects.all()
            activityLogSerializer = ListActivityLogSerializer(activityLog, many=True)
            return JsonResponse(activityLogSerializer.data, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'list'. Use GET.")
        
    elif method == 'view-auth':
        if request.method == 'GET':
            try:
                loginActivity_id = request.GET.get('id')  # Extract id from query parameters
                if not loginActivity_id:
                    return JsonResponse("Missing 'id' parameter.", status=400, safe=False)
                
                loginActivity = LoginActivity.objects.get(id=loginActivity_id)
                loginActivitySerializer = LoginActivitySerializer(loginActivity)
                return JsonResponse(loginActivitySerializer.data, safe=False)
            except LoginActivity.DoesNotExist:
                print(f"LoginActivity not found for id: {loginActivity_id}")
                return JsonResponse("LoginActivity not found.", safe=False)
            except Exception as e:
                print(f"Error: {e}")
                return JsonResponse("An error occurred.", status=500, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'view'. Use GET.")

    elif method == 'view-act':
        if request.method == 'GET':
            try:
                activityLog_id = request.GET.get('id')  # Extract id from query parameters
                if not activityLog_id:
                    return JsonResponse("Missing 'id' parameter.", status=400, safe=False)
                
                activityLog = ActivityLog.objects.get(id=activityLog_id)
                activityLogSerializer = ActivityLogSerializer(activityLog)
                return JsonResponse(activityLogSerializer.data, safe=False)
            except ActivityLog.DoesNotExist:
                print(f"ActivityLog not found for id: {activityLog_id}")
                return JsonResponse("ActivityLog not found.", safe=False)
            except Exception as e:
                print(f"Error: {e}")
                return JsonResponse("An error occurred.", status=500, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'view'. Use GET.")
