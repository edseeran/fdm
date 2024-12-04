from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.UserAccount.models import UserProfile
from apps.UserAccount.serializers import UserNameSerializer

# @csrf_exempt
@login_required
@permission_classes([IsAuthenticated])
def userNameApi(request, method=None, id=None):
    """
    API view to handle listing and viewing of UserProfiles with only user and name.
    
    Parameters:
    - method: The action to perform ('list' or 'view').
    - id: The ID of the user profile (used in 'view' method).
    
    Returns:
    - JsonResponse with the result of the operation or an error message.
    """

    user = request.user

    # Check if the request method is allowed
    if method not in ['list', 'view']:
        return HttpResponseBadRequest("Invalid request method.")

    # Handle 'list' method: Return all user profiles with user and name
    if method == 'list':
        if not request.user.has_perm('UserAccount.view_userprofile'):
            return JsonResponse("Permission denied.", status=403, safe=False)
        
        if request.method == 'GET':
            # Superuser: List all profiles
            if user.is_superuser:
                userProfiles = UserProfile.objects.all()
            elif user.is_staff:
                # Staff: List profiles from all groups they belong to
                user_groups = user.groups.all()
                userProfiles = UserProfile.objects.filter(user__groups__in=user_groups).distinct()
            else:
                # Regular users cannot list other users
                return JsonResponse("Permission denied.", status=403, safe=False)

            # Serialize the result using UserNameSerializer
            userProfileSerializer = UserNameSerializer(userProfiles, many=True)
            return JsonResponse(userProfileSerializer.data, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'list'. Use GET.")

    # Handle 'view' method: Return a specific user profile by ID
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
                    user_groups = user.groups.all()
                    userProfile = UserProfile.objects.get(id=userProfile_id, user__groups__in=user_groups)
                else:
                    # Regular users can only view their own profile
                    if userProfile_id != str(user.userprofile.id):
                        return JsonResponse("Permission denied.", status=403, safe=False)
                    userProfile = UserProfile.objects.get(id=userProfile_id)

                # Serialize the result using UserNameSerializer
                userProfileSerializer = UserNameSerializer(userProfile)
                return JsonResponse(userProfileSerializer.data, safe=False)
            except UserProfile.DoesNotExist:
                return JsonResponse("User Profile not found.", status=404, safe=False)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        else:
            return HttpResponseBadRequest("Invalid request method for 'view'. Use GET.")
