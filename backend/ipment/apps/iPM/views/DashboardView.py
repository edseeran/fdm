from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.iPM.models import Dashboard
from apps.iPM.serializers import DashboardSerializer
from apps.ActivityLog.models import ActivityLog
import json

# @csrf_exempt
@login_required
@permission_classes([IsAuthenticated])
def dashboardApi(request, method=None, id=None):
    """
    API view to handle Dashboard creation, listing, viewing, updating, and deletion.
    Implements activity logging for create, update, and delete operations.

    Parameters:
    - request: The HTTP request object.
    - method: The action to perform ('create', 'list', 'view', 'update', 'delete').
    - id: The ID of the Dashboard (not used directly as it's extracted from request data).

    Returns:
    - JsonResponse with the result of the operation or an error message.
    """

    if method not in ['create', 'list', 'view', 'update', 'delete']:
        return HttpResponseBadRequest("Invalid request method.")

    # Permission checks for different methods
    if method in ['list', 'view'] and not request.user.has_perm('iPM.view_dashboard'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'create' and not request.user.has_perm('iPM.add_dashboard'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'update' and not request.user.has_perm('iPM.change_dashboard'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'delete' and not request.user.has_perm('iPM.delete_dashboard'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    # Handle the 'create' method
    if method == 'create':
        if request.method == 'POST':
            dashboardData = JSONParser().parse(request)
            dashboardSerializer = DashboardSerializer(data=dashboardData)
            if dashboardSerializer.is_valid():
                dashboard = dashboardSerializer.save()

                # Log the creation of the Dashboard
                ActivityLog.objects.create(
                    user=request.user,
                    method='create',
                    module='iPM',
                    model='Dashboard',
                    record_id=dashboard.id,
                    changes='New Record'
                )

                return JsonResponse("Dashboard added Successfully.", safe=False)
            else:
                return JsonResponse({"errors": dashboardSerializer.errors}, status=400)
        else:
            return HttpResponseBadRequest("Invalid request method for 'create'. Use POST.")

    # Handle the 'list' method
    elif method == 'list':
        if request.method == 'GET':
            dashboards = Dashboard.objects.all()
            dashboardSerializer = DashboardSerializer(dashboards, many=True)
            return JsonResponse(dashboardSerializer.data, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'list'. Use GET.")

    # Handle the 'view' method
    elif method == 'view':
        if request.method == 'GET':
            try:
                dashboard_id = request.GET.get('id')  # Extract id from query parameters
                if not dashboard_id:
                    return JsonResponse("Missing 'id' parameter.", status=400, safe=False)

                dashboard = Dashboard.objects.get(id=dashboard_id)
                dashboardSerializer = DashboardSerializer(dashboard)
                return JsonResponse(dashboardSerializer.data, safe=False)
            except Dashboard.DoesNotExist:
                return JsonResponse("Dashboard not found.", safe=False)
            except Exception as e:
                return JsonResponse("An error occurred.", status=500, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'view'. Use GET.")

    # Handle the 'update' method
    elif method == 'update':
        if request.method == 'PUT':
            dashboardData = JSONParser().parse(request)
            dashboard_id = dashboardData.get('id', None)
            if not dashboard_id:
                return JsonResponse("Missing 'id' in request body.", status=400, safe=False)

            try:
                dashboard = Dashboard.objects.get(id=dashboard_id)

                # Serialize current data before update
                old_data = DashboardSerializer(dashboard).data

                dashboardSerializer = DashboardSerializer(dashboard, data=dashboardData, partial=True)
                if dashboardSerializer.is_valid():
                    dashboardSerializer.save()

                    # Serialize new data after update
                    new_data = DashboardSerializer(dashboard).data

                    # Compute changes
                    changes = {}
                    for field in dashboardData.keys():
                        old_value = old_data.get(field)
                        new_value = new_data.get(field)
                        if old_value != new_value:
                            changes[field] = {'from': old_value, 'to': new_value}

                    # Log the update
                    ActivityLog.objects.create(
                        user=request.user,
                        method='update',
                        module='iPM',
                        model='Dashboard',
                        record_id=dashboard.id,
                        changes=changes
                    )

                    return JsonResponse("Dashboard updated Successfully.", safe=False)
                else:
                    return JsonResponse({"errors": dashboardSerializer.errors}, status=400)
            except Dashboard.DoesNotExist:
                return JsonResponse("Dashboard not found.", safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'update'. Use PUT.")

    # Handle the 'delete' method
    elif method == 'delete':
        if request.method == 'DELETE':
            dashboardData = JSONParser().parse(request)
            dashboard_id = dashboardData.get('id', None)

            if dashboard_id is not None:
                try:
                    dashboard = Dashboard.objects.get(id=dashboard_id)
                    dashboard.delete()

                    # Log the deletion
                    ActivityLog.objects.create(
                        user=request.user,
                        method='delete',
                        module='iPM',
                        model='Dashboard',
                        record_id=dashboard_id,
                        changes='Record Deleted'
                    )

                    return JsonResponse("Dashboard deleted Successfully.", safe=False)
                except Dashboard.DoesNotExist:
                    return JsonResponse("Dashboard not found.", safe=False)
            else:
                return JsonResponse("Missing 'id' in request body.", safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'delete'. Use DELETE.")