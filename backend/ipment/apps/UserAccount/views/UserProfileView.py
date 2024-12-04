from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.UserAccount.models import UserProfile
from apps.UserAccount.serializers import UserProfileSerializer, UserProfileListSerializer
from django.contrib.auth.models import User
from apps.ActivityLog.models import ActivityLog  # Import the ActivityLog model
import json  # Import json module to handle changes field

# @csrf_exempt
@login_required
@permission_classes([IsAuthenticated])
def userProfileApi(request, method=None, id=None):
    """
    API view to handle UserProfile creation, listing, viewing, updating, and deletion.
    Implements activity logging for create, update, and delete operations.

    Parameters:
    - request: The HTTP request object.
    - method: The action to perform ('create', 'list', 'view', 'update', 'delete').
    - id: The ID of the user profile (not used directly as it's extracted from request data).

    Returns:
    - JsonResponse with the result of the operation or an error message.
    """

    user = request.user

    # Superuser: Full access without permission checks
    if user.is_superuser:
        pass

    # Staff: Must pass permission checks and group-based restrictions
    elif user.is_staff:
        user_groups = user.groups.all()  # Get all groups the staff member belongs to

    # Regular users: Must pass permission checks and can only manage their own profile
    else:
        if method not in ['create', 'view', 'update', 'delete']:
            return HttpResponseBadRequest("Invalid request method.")
        if method == 'create' and hasattr(user, 'userprofile'):
            return JsonResponse("Permission denied. You already have a profile.", status=403, safe=False)

    # Permission checks based on method for both staff and regular users
    if method == 'create':
        if not request.user.has_perm('UserAccount.add_userprofile'):
            return JsonResponse("Permission denied.", status=403, safe=False)
        if request.method == 'POST':
            userProfileData = JSONParser().parse(request)

            # Staff: Can only create profiles for users within their groups
            if user.is_staff:
                group_ids = user.groups.values_list('id', flat=True)
                target_user_id = userProfileData.get('user', None)
                if target_user_id:
                    target_user = User.objects.get(id=target_user_id)
                    target_user_group_ids = target_user.groups.values_list('id', flat=True)
                    if not any(group_id in group_ids for group_id in target_user_group_ids):
                        return JsonResponse("Permission denied. You can only create profiles for users within your groups.", status=403, safe=False)
                else:
                    return JsonResponse("Missing 'user' in request body.", status=400, safe=False)

            # Regular users: Can only create their own profile
            elif not user.is_superuser:
                userProfileData['user'] = user.id

            userProfileSerializer = UserProfileSerializer(data=userProfileData)
            if userProfileSerializer.is_valid():
                userProfile = userProfileSerializer.save()

                # Log the creation of UserProfile
                ActivityLog.objects.create(
                    user=request.user,
                    method='create',
                    module='UserAccount',
                    model='UserProfile',
                    record_id=userProfile.id,
                    changes='New Record'
                )

                return JsonResponse("UserProfile added Successfully.", safe=False)
            else:
                return JsonResponse({"errors": userProfileSerializer.errors}, status=400)
        else:
            return HttpResponseBadRequest("Invalid request method for 'create'. Use POST.")

    elif method == 'list':
        if not request.user.has_perm('UserAccount.view_userprofile'):
            return JsonResponse("Permission denied.", status=403, safe=False)
        if request.method == 'GET':
            # Superuser: List all profiles
            if user.is_superuser:
                userProfile = UserProfile.objects.all()
            elif user.is_staff:
                # Staff: List profiles from all groups they belong to
                userProfile = UserProfile.objects.filter(user__groups__in=user_groups).distinct()
            else:
                # Regular users cannot list other users
                return JsonResponse("Permission denied.", status=403, safe=False)

            userProfileListSerializer = UserProfileListSerializer(userProfile, many=True)
            return JsonResponse(userProfileListSerializer.data, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'list'. Use GET.")

    elif method == 'view':
        if not request.user.has_perm('UserAccount.view_userprofile'):
            return JsonResponse("Permission denied.", status=403, safe=False)
        if request.method == 'GET':
            try:
                userProfile_id = request.GET.get('id')
                if not userProfile_id:
                    return JsonResponse("Missing 'id' parameter.", status=400, safe=False)

                # Superuser: Can view any profile
                if user.is_superuser:
                    userProfile = UserProfile.objects.get(id=userProfile_id)
                elif user.is_staff:
                    # Staff: Can only view profiles within their groups
                    userProfile = UserProfile.objects.get(id=userProfile_id, user__groups__in=user_groups)
                else:
                    # Regular users can only view their own profile
                    if userProfile_id != str(user.userprofile.id):
                        return JsonResponse("Permission denied.", status=403, safe=False)
                    userProfile = UserProfile.objects.get(id=userProfile_id)

                userProfileSerializer = UserProfileSerializer(userProfile)
                return JsonResponse(userProfileSerializer.data, safe=False)
            except UserProfile.DoesNotExist:
                return JsonResponse("User Profile not found.", safe=False)
            except Exception as e:
                return JsonResponse("An error occurred.", status=500, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'view'. Use GET.")

    elif method == 'update':
        if not request.user.has_perm('UserAccount.change_userprofile'):
            return JsonResponse("Permission denied.", status=403, safe=False)
        if request.method == 'PUT':
            userProfileData = JSONParser().parse(request)
            userProfile_id = userProfileData.get('id', None)

            if not userProfile_id:
                return JsonResponse("Missing 'id' in request body.", status=400, safe=False)

            try:
                # Superuser: Can update any profile
                if user.is_superuser:
                    userProfile = UserProfile.objects.get(id=userProfile_id)
                elif user.is_staff:
                    # Staff: Can only update profiles within their groups
                    userProfile = UserProfile.objects.get(id=userProfile_id, user__groups__in=user_groups)
                else:
                    # Regular users can only update their own profile
                    if userProfile_id != str(user.userprofile.id):
                        return JsonResponse("Permission denied.", status=403, safe=False)
                    userProfile = UserProfile.objects.get(id=userProfile_id)

                # Serialize current data before update
                old_userprofile_data = UserProfileSerializer(userProfile).data

                userProfileSerializer = UserProfileSerializer(userProfile, data=userProfileData, partial=True)
                if userProfileSerializer.is_valid():
                    userProfileSerializer.save()

                    # Serialize new data after update
                    new_userprofile_data = UserProfileSerializer(userProfile).data

                    # Compute changes
                    changes = {}
                    for field in userProfileData.keys():
                        old_value = old_userprofile_data.get(field)
                        new_value = new_userprofile_data.get(field)
                        if old_value != new_value:
                            changes[field] = {'from': old_value, 'to': new_value}

                    # Log the update
                    ActivityLog.objects.create(
                        user=request.user,
                        method='update',
                        module='UserAccount',
                        model='UserProfile',
                        record_id=userProfile.id,
                        changes=changes
                    )

                    return JsonResponse("UserProfile updated Successfully.", safe=False)
                else:
                    return JsonResponse({"errors": userProfileSerializer.errors}, status=400)
            except UserProfile.DoesNotExist:
                return JsonResponse("User Profile not found.", safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'update'. Use PUT.")

    elif method == 'delete':
        if not request.user.has_perm('UserAccount.delete_userprofile'):
            return JsonResponse("Permission denied.", status=403, safe=False)
        if request.method == 'DELETE':
            userProfileData = JSONParser().parse(request)
            userProfile_id = userProfileData.get('id', None)

            if not userProfile_id:
                return JsonResponse("Missing 'id' in request body.", status=400, safe=False)

            try:
                # Superuser: Can delete any profile
                if user.is_superuser:
                    userProfile = UserProfile.objects.get(id=userProfile_id)
                elif user.is_staff:
                    # Staff: Can only delete profiles within their groups
                    userProfile = UserProfile.objects.get(id=userProfile_id, user__groups__in=user_groups)
                else:
                    # Regular users can only delete their own profile
                    if userProfile_id != str(user.userprofile.id):
                        return JsonResponse("Permission denied.", status=403, safe=False)
                    userProfile = UserProfile.objects.get(id=userProfile_id)

                userProfile.delete()

                # Log the deletion
                ActivityLog.objects.create(
                    user=request.user,
                    method='delete',
                    module='UserAccount',
                    model='UserProfile',
                    record_id=userProfile_id,
                    changes='Record Deleted'
                )

                return JsonResponse("UserProfile deleted Successfully.", safe=False)
            except UserProfile.DoesNotExist:
                return JsonResponse("User Profile not found.", safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'delete'. Use DELETE.")
