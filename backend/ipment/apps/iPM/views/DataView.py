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
from apps.Configuration.models import MeasurementUnit, Label
from django.utils.dateparse import parse_datetime
from django.db.models import Avg, Q
import json


def convert_rate(rate, unit):
    """Helper function to convert rate based on measurement unit."""
    if unit == 'bit':
        return rate
    elif unit == 'kilobit':
        return rate / 1000
    elif unit == 'megabit':
        return rate / (10 ** 6)
    elif unit == 'byte':
        return rate / 8
    elif unit == 'kilobyte':
        return rate / (8 * 10 ** 3)
    elif unit == 'megabyte':
        return rate / (8 * 10 ** 6)
    else:
        return rate  # Default to bit if the unit is unrecognized


def get_measurement_unit():
    """Helper function to get measurement unit with id=1. Defaults to 'bit' if not found."""
    try:
        measurement_unit = MeasurementUnit.objects.get(id=1)
        return measurement_unit.unit
    except MeasurementUnit.DoesNotExist:
        print("Warning: MeasurementUnit with id=1 not found. Defaulting to 'bit'.")
        return 'bit'  # Default to 'bit' if the record does not exist


def get_label_for_circuit(name):
    """Helper function to find label for a given circuit name."""
    try:
        label = Label.objects.get(circuit=name)
        return label.label
    except Label.DoesNotExist:
        return name  # Return the original name if no label is found


def get_circuit_from_label_or_name(circuit_or_label):
    """Helper function to get the 'name' (circuit) from either a given label or name."""
    try:
        # Check if the parameter is a label, and get the corresponding 'circuit' (name)
        label = Label.objects.get(label=circuit_or_label)
        return label.circuit
    except Label.DoesNotExist:
        # If it's not a label, treat it as the circuit (name)
        return circuit_or_label


def filter_queryset_for_user(user, data_queryset):
    """
    Helper function to filter the queryset based on user permissions.
    - If user is superuser or in the 'Administrator' group, return all data.
    - Otherwise, filter data based on the dashboards connected to the user.
    """
    if user.is_superuser or user.groups.filter(name='Administrator').exists():
        return data_queryset  # User can see all records
    else:
        try:
            # Get user's dashboards and call .all() to retrieve related objects
            user_profile = UserProfile.objects.get(user=user)
            dashboard_ids = user_profile.dashboards.all()  # FIX: Properly query related dashboards
            dashboards = Dashboard.objects.filter(id__in=dashboard_ids)
            data_names = []
            for dashboard in dashboards:
                data_field = dashboard.data  # Assuming 'data' is a list
                data_names.extend(data_field)
            data_names = [name.lower() for name in data_names]

            # Filter Data records that match any of the dashboard's data (case-insensitive, contains)
            query = Q()
            for name in data_names:
                query |= Q(name__icontains=name)
            
            return data_queryset.filter(query)

        except UserProfile.DoesNotExist:
            return Data.objects.none()  # If user profile is missing, return no records


@login_required
@permission_classes([IsAuthenticated])
def dataApi(request, method=None):
    """
    API view to handle Data listing and deletion.
    """

    if method not in ['list', 'list-top', 'list-circuit', 'delete']:
        return HttpResponseBadRequest("Invalid request method.")

    user = request.user

    # Handle the 'list-circuit' method
    if method == 'list-circuit':
        if request.method == 'GET':
            # Get all unique name fields from Data model
            data_queryset = Data.objects.values_list('name', flat=True).distinct()

            # Filter queryset based on user permissions
            data_queryset = filter_queryset_for_user(user, data_queryset)

            # Optionally, you can replace the circuit names with labels from the Label model
            circuits_with_labels = [get_label_for_circuit(name) for name in data_queryset]

            # Return unique list of circuits/labels
            return JsonResponse(list(set(circuits_with_labels)), safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'list-circuit'. Use GET.")

    # Handle the 'list' method
    if method == 'list':
        if request.method == 'GET':
            # Get filter parameters
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            circuit_or_label = request.GET.get('circuit')

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
            
            if circuit_or_label:
                # If circuit_or_label is provided, get the corresponding circuit (name)
                circuit = get_circuit_from_label_or_name(circuit_or_label)
                data_queryset = data_queryset.filter(name__icontains=circuit)

            # Filter queryset based on user permissions
            data_queryset = filter_queryset_for_user(user, data_queryset)

            # Get the measurement unit and apply rate conversion if necessary
            measurement_unit = get_measurement_unit()

            # Annotate and aggregate data
            data_queryset = data_queryset.order_by('time')
            dataSerializer = DataSerializer(data_queryset, many=True)

            results = []
            for item in dataSerializer.data:
                # Convert the rates based on measurement unit
                inbound_rate = convert_rate(float(item['inbound_rate']), measurement_unit)
                outbound_rate = convert_rate(float(item['outbound_rate']), measurement_unit)

                # Round the rates to 3 decimal places
                inbound_rate = round(inbound_rate, 3)
                outbound_rate = round(outbound_rate, 3)

                # Map the name to the label from Label model
                name = get_label_for_circuit(item['name'])

                # Append the modified data to the results
                results.append({
                    'id': item['id'],
                    'name': name,
                    'inbound_rate': inbound_rate,
                    'outbound_rate': outbound_rate,
                    'time': item['time'],
                })

            return JsonResponse(results, safe=False)

    # Handle the 'list-top' method
    elif method == 'list-top':
        if request.method == 'GET':
            # Get parameters
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            top_n = request.GET.get('top_n', 10)
            order_by = request.GET.get('order_by', 'desc')
            value_param = request.GET.get('value', 'outbound_rate')

            # Validate 'value_param'
            if value_param not in ['inbound_rate', 'outbound_rate']:
                return JsonResponse(
                    "Invalid 'value' parameter. Must be 'inbound_rate' or 'outbound_rate'.",
                    status=400,
                    safe=False
                )

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
                return JsonResponse(
                    "Invalid 'order_by' parameter. Must be 'asc' or 'desc'.",
                    status=400,
                    safe=False
                )

            # Convert top_n to int
            try:
                top_n = int(top_n)
            except ValueError:
                return JsonResponse(
                    "Invalid 'top_n' parameter. Must be an integer.",
                    status=400,
                    safe=False
                )

            # Filter Data objects
            data_queryset = Data.objects.all()
            if start_date and end_date:
                data_queryset = data_queryset.filter(time__range=(start_date, end_date))

            # Filter queryset based on user permissions
            data_queryset = filter_queryset_for_user(user, data_queryset)

            # Get the measurement unit and provide a default value if None
            measurement_unit = get_measurement_unit()  # It will now default to 'bit' if not found

            # Group by 'name' and compute average of rates
            data_aggregated = data_queryset.values('name').annotate(
                avg_inbound_rate=Avg('inbound_rate'),
                avg_outbound_rate=Avg('outbound_rate')
            )

            order_field = 'avg_' + value_param
            if order_by == 'asc':
                data_aggregated = data_aggregated.order_by(order_field)
            else:
                data_aggregated = data_aggregated.order_by('-' + order_field)

            data_aggregated = data_aggregated[:top_n]

            results = []
            for idx, item in enumerate(data_aggregated, start=1):
                # Convert the rates based on measurement unit
                avg_inbound_rate = convert_rate(float(item['avg_inbound_rate']), measurement_unit)
                avg_outbound_rate = convert_rate(float(item['avg_outbound_rate']), measurement_unit)

                # Round the rates to 3 decimal places
                avg_inbound_rate = round(avg_inbound_rate, 3)
                avg_outbound_rate = round(avg_outbound_rate, 3)

                # Map the name to the label from Label model
                name = get_label_for_circuit(item['name'])

                # Append the modified data to the results
                results.append({
                    'index': idx,
                    'name': name,
                    'avg_inbound_rate': avg_inbound_rate,
                    'avg_outbound_rate': avg_outbound_rate
                })

            return JsonResponse(results, safe=False)

    # Handle the 'delete' method
    elif method == 'delete':
        if not user.is_superuser and not user.groups.filter(name='Administrator').exists():
            return JsonResponse("Permission denied.", status=403, safe=False)
        if request.method == 'DELETE':
            # Get parameters from query string
            data_id = request.GET.get('id', None)
            circuit_or_label = request.GET.get('circuit', None)
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
            elif circuit_or_label:
                # Get the circuit (name) from either label or name
                circuit = get_circuit_from_label_or_name(circuit_or_label)
                # Filter queryset based on user permissions
                data_queryset = filter_queryset_for_user(user, Data.objects.filter(name__icontains=circuit))
                
                count_deleted = data_queryset.count()
                if count_deleted == 0:
                    return JsonResponse("Data not found.", safe=False)
                ids_deleted = list(data_queryset.values_list('id', flat=True))
                data_queryset.delete()
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
                # Filter queryset based on user permissions
                data_queryset = filter_queryset_for_user(user, Data.objects.filter(time__range=(start_date, end_date)))

                count_deleted = data_queryset.count()
                if count_deleted == 0:
                    return JsonResponse("Data not found.", safe=False)
                ids_deleted = list(data_queryset.values_list('id', flat=True))
                data_queryset.delete()
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
