from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.UserAccount.models import Permission
from apps.UserAccount.serializers import PermissionSerializer, PermissionListSerializer

# @csrf_exempt
@login_required
@permission_classes([IsAuthenticated])
def permissionApi(request, method=None, id=None):
    if method not in ['list', 'view']:
        return HttpResponseBadRequest("Invalid request method.")

    # Permission check for view method
    if method in ['list', 'view'] and not request.user.has_perm('UserAccount.view_permission'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'list':
        if request.method == 'GET':
            permissions = Permission.objects.all()
            permissionSerializer = PermissionListSerializer(permissions, many=True)
            return JsonResponse(permissionSerializer.data, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'list'. Use GET.")
        
    elif method == 'view':
        if request.method == 'GET':
            try:
                permission_id = request.GET.get('id')  # Extract id from query parameters
                if not permission_id:
                    return JsonResponse("Missing 'id' parameter.", status=400, safe=False)
                
                permission = Permission.objects.get(id=permission_id)
                permissionSerializer = PermissionSerializer(permission)
                return JsonResponse(permissionSerializer.data, safe=False)
            except Permission.DoesNotExist:
                print(f"Permission not found for id: {permission_id}")
                return JsonResponse("Permission not found.", safe=False)
            except Exception as e:
                print(f"Error: {e}")
                return JsonResponse("An error occurred.", status=500, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'view'. Use GET.")
