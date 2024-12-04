from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group  # Use Django's built-in Group model
from apps.UserAccount.serializers import GroupSerializer, GroupListSerializer
from apps.ActivityLog.models import ActivityLog  # Import ActivityLog model
import json  # Import json module for handling changes

@login_required
@permission_classes([IsAuthenticated])
def groupApi(request, method=None, id=None):
    """
    API view to handle Group creation, listing, viewing, updating, and deletion.
    Implements activity logging for create, update, and delete operations.

    Parameters:
    - request: The HTTP request object.
    - method: The action to perform ('create', 'list', 'view', 'update', 'delete').
    - id: The ID of the group (not used directly as it's extracted from request data).

    Returns:
    - JsonResponse with the result of the operation or an error message.
    """

    if method not in ['create', 'list', 'view', 'update', 'delete']:
        return HttpResponseBadRequest("Invalid request method.")

    # Permission checks for different methods
    if method in ['list', 'view'] and not request.user.has_perm('auth.view_group'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'create' and not request.user.has_perm('auth.add_group'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'update' and not request.user.has_perm('auth.change_group'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'delete' and not request.user.has_perm('auth.delete_group'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    # Handle the 'create' method
    if method == 'create':
        if request.method == 'POST':
            groupData = JSONParser().parse(request)
            groupSerializer = GroupSerializer(data=groupData)
            if groupSerializer.is_valid():
                group = groupSerializer.save()

                # Log the creation of the Group
                ActivityLog.objects.create(
                    user=request.user,
                    method='create',
                    module='UserAccount',
                    model='Group',
                    record_id=group.id,
                    changes='New Record'
                )

                return JsonResponse("Group added Successfully.", safe=False)
            else:
                return JsonResponse({"errors": groupSerializer.errors}, status=400)
        else:
            return HttpResponseBadRequest("Invalid request method for 'create'. Use POST.")

    # Handle the 'list' method
    elif method == 'list':
        if request.method == 'GET':
            groups = Group.objects.all()
            groupSerializer = GroupListSerializer(groups, many=True)
            return JsonResponse(groupSerializer.data, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'list'. Use GET.")

    # Handle the 'view' method
    elif method == 'view':
        if request.method == 'GET':
            try:
                group_id = request.GET.get('id')  # Extract id from query parameters
                if not group_id:
                    return JsonResponse("Missing 'id' parameter.", status=400, safe=False)

                group = Group.objects.get(id=group_id)
                groupSerializer = GroupSerializer(group)
                return JsonResponse(groupSerializer.data, safe=False)
            except Group.DoesNotExist:
                return JsonResponse("Group not found.", safe=False)
            except Exception as e:
                return JsonResponse("An error occurred.", status=500, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'view'. Use GET.")

    # Handle the 'update' method
    elif method == 'update':
        if request.method == 'PUT':
            groupData = JSONParser().parse(request)
            group_id = groupData.get('id', None)
            if not group_id:
                return JsonResponse("Missing 'id' in request body.", status=400, safe=False)

            try:
                group = Group.objects.get(id=group_id)

                # Serialize current data before update
                old_group_data = GroupSerializer(group).data

                groupSerializer = GroupSerializer(group, data=groupData, partial=True)
                if groupSerializer.is_valid():
                    groupSerializer.save()

                    # Serialize new data after update
                    new_group_data = GroupSerializer(group).data

                    # Compute changes
                    changes = {}
                    for field in groupData.keys():
                        old_value = old_group_data.get(field)
                        new_value = new_group_data.get(field)
                        if old_value != new_value:
                            changes[field] = {'from': old_value, 'to': new_value}

                    # Log the update
                    ActivityLog.objects.create(
                        user=request.user,
                        method='update',
                        module='UserAccount',
                        model='Group',
                        record_id=group.id,
                        changes=changes
                    )

                    return JsonResponse("Group updated Successfully.", safe=False)
                else:
                    return JsonResponse({"errors": groupSerializer.errors}, status=400)
            except Group.DoesNotExist:
                return JsonResponse("Group not found.", safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'update'. Use PUT.")

    # Handle the 'delete' method
    elif method == 'delete':
        if request.method == 'DELETE':
            groupData = JSONParser().parse(request)
            group_id = groupData.get('id', None)

            if group_id is not None:
                try:
                    group = Group.objects.get(id=group_id)
                    group.delete()

                    # Log the deletion
                    ActivityLog.objects.create(
                        user=request.user,
                        method='delete',
                        module='UserAccount',
                        model='Group',
                        record_id=group_id,
                        changes='Record Deleted'
                    )

                    return JsonResponse("Group deleted Successfully.", safe=False)
                except Group.DoesNotExist:
                    return JsonResponse("Group not found.", safe=False)
            else:
                return JsonResponse("Missing 'id' in request body.", safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'delete'. Use DELETE.")
