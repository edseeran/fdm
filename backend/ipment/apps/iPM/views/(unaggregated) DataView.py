from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.iPM.models import Data, Dashboard
from apps.iPM.serializers import DataSerializer
from apps.ActivityLog.models import ActivityLog
from django.contrib.auth.models import Group
from apps.UserAccount.models import UserProfile
from django.utils.dateparse import parse_datetime
from django.db.models import Avg, Q
import json

@login_required
@permission_classes([IsAuthenticated])
def dataApi(request, method=None):
    """
    API view to handle Data listing and deletion.
    """

    if method not in ['list', 'list-top', 'delete']:
        return HttpResponseBadRequest("Invalid request method.")

    user = request.user

    # Handle the 'list' method
    if method == 'list':
        if request.method == 'GET':
            # Get filter parameters
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            circuit = request.GET.get('circuit')

            # Apply default values
            latest_time = Data.objects.latest('time').time if Data.objects.exists() else None
            if not start_date:
                start_date = latest_time
            if not end_date:
                end_date = latest_time

            # Convert start_date and end_date to datetime objects
            try:
                start_date = parse_datetime(start_date)
                end_date = parse_datetime(end_date)
            except:
                return JsonResponse("Invalid date format.", status=400, safe=False)

            # Filter Data objects
            data_queryset = Data.objects.all()
            if start_date and end_date:
                data_queryset = data_queryset.filter(time__range=(start_date, end_date))
            if circuit:
                data_queryset = data_queryset.filter(name__icontains=circuit)

            # Permissions handling
            if user.is_superuser or user.groups.filter(name='Administrator').exists():
                pass  # User can see all records
            else:
                try:
                    # Get user's dashboards
                    user_profile = UserProfile.objects.get(user=user)
                    dashboard_ids = user_profile.dashboards
                    dashboards = Dashboard.objects.filter(id__in=dashboard_ids)
                    data_names = []
                    for dashboard in dashboards:
                        data_field = dashboard.data  # Assuming 'data' is a list
                        data_names.extend(data_field)
                    data_names = [name.lower() for name in data_names]
                    # Filter Data records
                    data_queryset = data_queryset.filter(name__in=data_names)
                except UserProfile.DoesNotExist:
                    return JsonResponse("User profile not found.", status=400, safe=False)

            # Serialize and return
            dataSerializer = DataSerializer(data_queryset, many=True)
            return JsonResponse(dataSerializer.data, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'list'. Use GET.")

    # Handle the 'list-top' method
    elif method == 'list-top':
        if request.method == 'GET':
            # Get parameters
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            top_n = request.GET.get('top_n', 10)
            order_by = request.GET.get('order_by', 'desc')

            # Apply defaults
            latest_time = Data.objects.latest('time').time if Data.objects.exists() else None
            if not start_date:
                start_date = latest_time
            if not end_date:
                end_date = latest_time

            # Convert start_date and end_date to datetime objects
            try:
                start_date = parse_datetime(start_date)
                end_date = parse_datetime(end_date)
            except:
                return JsonResponse("Invalid date format.", status=400, safe=False)

            # Validate 'order_by' parameter
            if order_by not in ['asc', 'desc']:
                return JsonResponse("Invalid 'order_by' parameter. Must be 'asc' or 'desc'.", status=400, safe=False)

            # Convert top_n to int
            try:
                top_n = int(top_n)
            except ValueError:
                return JsonResponse("Invalid 'top_n' parameter. Must be an integer.", status=400, safe=False)

            # Filter Data objects
            data_queryset = Data.objects.all()
            if start_date and end_date:
                data_queryset = data_queryset.filter(time__range=(start_date, end_date))

            # Permissions handling
            if user.is_superuser or user.groups.filter(name='Administrator').exists():
                pass  # User can see all records
            else:
                try:
                    # Get user's dashboards
                    user_profile = UserProfile.objects.get(user=user)
                    dashboard_ids = user_profile.dashboards
                    dashboards = Dashboard.objects.filter(id__in=dashboard_ids)
                    data_names = []
                    for dashboard in dashboards:
                        data_field = dashboard.data  # Assuming 'data' is a list
                        data_names.extend(data_field)
                    data_names = [name.lower() for name in data_names]
                    # Filter Data records
                    data_queryset = data_queryset.filter(name__in=data_names)
                except UserProfile.DoesNotExist:
                    return JsonResponse("User profile not found.", status=400, safe=False)

            # Group by 'name' and compute average of 'inbound_rate' and 'outbound_rate'
            data_aggregated = data_queryset.values('name').annotate(
                avg_inbound_rate=Avg('inbound_rate'),
                avg_outbound_rate=Avg('outbound_rate')
            )

            # Order the results based on avg_outbound_rate by default
            if order_by == 'asc':
                data_aggregated = data_aggregated.order_by('avg_outbound_rate')
            else:
                data_aggregated = data_aggregated.order_by('-avg_outbound_rate')

            # Limit to top_n
            data_aggregated = data_aggregated[:top_n]

            # Add index to the results
            results = []
            for index, item in enumerate(data_aggregated, start=1):
                results.append({
                    'index': index,
                    'name': item['name'],
                    'avg_inbound_rate': item['avg_inbound_rate'],
                    'avg_outbound_rate': item['avg_outbound_rate']
                })

            # Return the results
            return JsonResponse(results, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'list-top'. Use GET.")

    # Handle the 'delete' method
    elif method == 'delete':
        if not user.is_superuser and not user.groups.filter(name='Administrator').exists():
            return JsonResponse("Permission denied.", status=403, safe=False)
        if request.method == 'DELETE':
            # Get parameters from query string
            data_id = request.GET.get('id', None)
            circuit = request.GET.get('circuit', None)
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')

            # If only one of start_date or end_date is provided, use it for both
            if start_date and not end_date:
                end_date = start_date
            if end_date and not start_date:
                start_date = end_date

            # Convert start_date and end_date to datetime objects
            if start_date and end_date:
                try:
                    start_date = parse_datetime(start_date)
                    end_date = parse_datetime(end_date)
                except:
                    return JsonResponse("Invalid date format.", status=400, safe=False)

            # Determine delete method based on priority: id > circuit > date range
            if data_id:
                # Delete single record by id
                try:
                    data = Data.objects.get(id=data_id)
                    data.delete()
                    # Log the deletion
                    ActivityLog.objects.create(
                        user=user,
                        method='delete',
                        module='iPM',
                        model='Data',
                        record_id=data_id,
                        changes='Record Deleted'
                    )
                    return JsonResponse("Data deleted successfully.", safe=False)
                except Data.DoesNotExist:
                    return JsonResponse("Data not found.", safe=False)
            elif circuit:
                # Delete records where name contains circuit (case-insensitive)
                data_to_delete = Data.objects.filter(name__icontains=circuit)
                count_deleted = data_to_delete.count()
                if count_deleted == 0:
                    return JsonResponse("Data not found.", safe=False)
                ids_deleted = list(data_to_delete.values_list('id', flat=True))
                data_to_delete.delete()
                # Log the deletion
                ActivityLog.objects.create(
                    user=user,
                    method='delete',
                    module='iPM',
                    model='Data',
                    changes=f"{count_deleted} records with name containing '{circuit}' deleted. IDs: {ids_deleted}"
                )
                return JsonResponse(f"{count_deleted} record(s) deleted successfully.", safe=False)
            elif start_date and end_date:
                # Delete records within the time range
                data_to_delete = Data.objects.filter(time__range=(start_date, end_date))
                count_deleted = data_to_delete.count()
                if count_deleted == 0:
                    return JsonResponse("Data not found.", safe=False)
                ids_deleted = list(data_to_delete.values_list('id', flat=True))
                data_to_delete.delete()
                # Log the deletion
                ActivityLog.objects.create(
                    user=user,
                    method='delete',
                    module='iPM',
                    model='Data',
                    changes=f"{count_deleted} records between {start_date} and {end_date} deleted. IDs: {ids_deleted}"
                )
                return JsonResponse(f"{count_deleted} record(s) deleted successfully.", safe=False)
            else:
                return JsonResponse("No valid parameters provided for deletion.", safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'delete'. Use DELETE.")
