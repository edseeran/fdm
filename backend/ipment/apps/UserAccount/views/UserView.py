from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from apps.UserAccount.serializers import UserSerializer, UserListSerializer
from apps.ActivityLog.models import ActivityLog  # Import the ActivityLog model
import json  # Import json module to handle changes field

# @csrf_exempt
@login_required
@permission_classes([IsAuthenticated])
def userApi(request, method=None, id=None):
    """
    API view to handle User creation, listing, viewing, updating, and deletion.
    Implements activity logging for create, update, and delete operations.

    Parameters:
    - request: The HTTP request object.
    - method: The action to perform ('create', 'list', 'view', 'update', 'delete').
    - id: The ID of the user (not used directly as it's extracted from request data).

    Returns:
    - JsonResponse with the result of the operation or an error message.
    """

    if method not in ['create', 'list', 'view', 'update', 'delete']:
        return HttpResponseBadRequest("Invalid request method.")

    # Permission checks for different methods
    if method in ['list', 'view'] and not request.user.has_perm('auth.view_user'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'create' and not request.user.has_perm('auth.add_user'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'update' and not request.user.has_perm('auth.change_user'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'delete' and not request.user.has_perm('auth.delete_user'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    # Handle the 'create' method
    if method == 'create':
        if request.method == 'POST':
            userData = JSONParser().parse(request)
            userSerializer = UserSerializer(data=userData)
            if userSerializer.is_valid():
                user = userSerializer.save()  # Save the User instance

                # Log the creation of the User
                ActivityLog.objects.create(
                    user=request.user,
                    method='create',
                    module='UserAccount',
                    model='User',
                    record_id=user.id,
                    changes='New Record'
                )

                # UserProfile is automatically created via signals, and logging is handled there
                return JsonResponse("User added Successfully.", safe=False)
            else:
                return JsonResponse({"errors": userSerializer.errors}, status=400)
        else:
            return HttpResponseBadRequest("Invalid request method for 'create'. Use POST.")

    # Handle the 'list' method
    elif method == 'list':
        if request.method == 'GET':
            users = User.objects.all()
            userSerializer = UserListSerializer(users, many=True)
            return JsonResponse(userSerializer.data, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'list'. Use GET.")

    # Handle the 'view' method
    elif method == 'view':
        if request.method == 'GET':
            try:
                user_id = request.GET.get('id')  # Extract id from query parameters
                if not user_id:
                    return JsonResponse("Missing 'id' parameter.", status=400, safe=False)

                user = User.objects.get(id=user_id)
                userSerializer = UserSerializer(user)
                return JsonResponse(userSerializer.data, safe=False)
            except User.DoesNotExist:
                return JsonResponse("User not found.", safe=False)
            except Exception as e:
                return JsonResponse("An error occurred.", status=500, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'view'. Use GET.")

    # Handle the 'update' method
    elif method == 'update':
        if request.method == 'PUT':
            userData = JSONParser().parse(request)
            user_id = userData.get('id', None)
            if not user_id:
                return JsonResponse("Missing 'id' in request body.", status=400, safe=False)

            try:
                user = User.objects.get(id=user_id)

                # Serialize current data before update
                old_user_data = UserSerializer(user).data

                userSerializer = UserSerializer(user, data=userData, partial=True)
                if userSerializer.is_valid():
                    userSerializer.save()

                    # Serialize new data after update
                    new_user_data = UserSerializer(user).data

                    # Compute changes
                    changes = {}
                    for field in userData.keys():
                        old_value = old_user_data.get(field)
                        new_value = new_user_data.get(field)
                        if old_value != new_value:
                            changes[field] = {'from': old_value, 'to': new_value}

                    # Log the update
                    ActivityLog.objects.create(
                        user=request.user,
                        method='update',
                        module='UserAccount',
                        model='User',
                        record_id=user.id,
                        changes=changes
                    )

                    return JsonResponse("User updated Successfully.", safe=False)
                else:
                    return JsonResponse({"errors": userSerializer.errors}, status=400)
            except User.DoesNotExist:
                return JsonResponse("User not found.", safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'update'. Use PUT.")

    # Handle the 'delete' method
    elif method == 'delete':
        if request.method == 'DELETE':
            userData = JSONParser().parse(request)
            user_id = userData.get('id', None)

            if user_id is not None:
                try:
                    user = User.objects.get(id=user_id)
                    user.delete()

                    # Log the deletion of the User
                    ActivityLog.objects.create(
                        user=request.user,
                        method='delete',
                        module='UserAccount',
                        model='User',
                        record_id=user_id,
                        changes='Record Deleted'
                    )

                    # UserProfile deletion and its logging are handled via signals
                    return JsonResponse("User deleted Successfully.", safe=False)
                except User.DoesNotExist:
                    return JsonResponse("User not found.", safe=False)
            else:
                return JsonResponse("Missing 'id' in request body.", safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'delete'. Use DELETE.")
