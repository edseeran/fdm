from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.Configuration.models import MeasurementUnit
from apps.Configuration.serializers import MeasurementUnitSerializer
from apps.ActivityLog.models import ActivityLog
from django.db import connection
import json

# @csrf_exempt
@login_required
@permission_classes([IsAuthenticated])
def measurementUnitApi(request, method=None, id=None):
    """
    API view to handle MeasurementUnit creation, listing, viewing, updating, and deletion.
    Only allows one MeasurementUnit record at a time. After a record is created, only updates 
    are allowed until the record is deleted. On deletion, ID resets to 1 for the next creation.

    Parameters:
    - request: The HTTP request object.
    - method: The action to perform ('create', 'list', 'view', 'update', 'delete').
    - id: The ID of the MeasurementUnit (not used directly as it's extracted from request data).

    Returns:
    - JsonResponse with the result of the operation or an error message.
    """

    if method not in ['create', 'list', 'view', 'update', 'delete']:
        return HttpResponseBadRequest("Invalid request method.")

    # Permission checks for different methods
    if method in ['list', 'view'] and not request.user.has_perm('Configuration.view_measurementunit'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'create' and not request.user.has_perm('Configuration.add_measurementunit'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'update' and not request.user.has_perm('Configuration.change_measurementunit'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'delete' and not request.user.has_perm('Configuration.delete_measurementunit'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    # Check if a record already exists before allowing 'create'
    if method == 'create':
        if request.method == 'POST':
            # Check if a MeasurementUnit record already exists
            if MeasurementUnit.objects.exists():
                return JsonResponse("Record already exists. Please update the existing record.", status=400, safe=False)

            # Parse request data
            measurementUnitData = JSONParser().parse(request)
            measurementUnitSerializer = MeasurementUnitSerializer(data=measurementUnitData)
            if measurementUnitSerializer.is_valid():
                # Save the new record
                measurementUnit = measurementUnitSerializer.save()

                # Log the creation of the MeasurementUnit
                ActivityLog.objects.create(
                    user=request.user,
                    method='create',
                    module='Configuration',
                    model='MeasurementUnit',
                    record_id=measurementUnit.id,
                    changes='New Record'
                )

                return JsonResponse("Measurement Unit added successfully.", safe=False)
            else:
                return JsonResponse({"errors": measurementUnitSerializer.errors}, status=400)
        else:
            return HttpResponseBadRequest("Invalid request method for 'create'. Use POST.")

    # Handle the 'list' method
    elif method == 'list':
        if request.method == 'GET':
            measurementUnits = MeasurementUnit.objects.all()
            measurementUnitSerializer = MeasurementUnitSerializer(measurementUnits, many=True)
            return JsonResponse(measurementUnitSerializer.data, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'list'. Use GET.")

    # Handle the 'view' method
    elif method == 'view':
        if request.method == 'GET':
            try:
                measurementUnit_id = request.GET.get('id')  # Extract id from query parameters
                if not measurementUnit_id:
                    return JsonResponse("Missing 'id' parameter.", status=400, safe=False)

                measurementUnit = MeasurementUnit.objects.get(id=measurementUnit_id)
                measurementUnitSerializer = MeasurementUnitSerializer(measurementUnit)
                return JsonResponse(measurementUnitSerializer.data, safe=False)
            except MeasurementUnit.DoesNotExist:
                return JsonResponse("Measurement Unit not found.", safe=False)
            except Exception as e:
                return JsonResponse("An error occurred.", status=500, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'view'. Use GET.")

    # Handle the 'update' method
    elif method == 'update':
        if request.method == 'PUT':
            measurementUnitData = JSONParser().parse(request)
            measurementUnit_id = measurementUnitData.get('id', None)
            if not measurementUnit_id:
                return JsonResponse("Missing 'id' in request body.", status=400, safe=False)

            try:
                measurementUnit = MeasurementUnit.objects.get(id=measurementUnit_id)

                # Serialize current data before update
                old_data = MeasurementUnitSerializer(measurementUnit).data

                measurementUnitSerializer = MeasurementUnitSerializer(measurementUnit, data=measurementUnitData, partial=True)
                if measurementUnitSerializer.is_valid():
                    measurementUnitSerializer.save()

                    # Serialize new data after update
                    new_data = MeasurementUnitSerializer(measurementUnit).data

                    # Compute changes
                    changes = {}
                    for field in measurementUnitData.keys():
                        old_value = old_data.get(field)
                        new_value = new_data.get(field)
                        if old_value != new_value:
                            changes[field] = {'from': old_value, 'to': new_value}

                    # Log the update
                    ActivityLog.objects.create(
                        user=request.user,
                        method='update',
                        module='Configuration',
                        model='MeasurementUnit',
                        record_id=measurementUnit.id,
                        changes=changes
                    )

                    return JsonResponse("Measurement Unit updated successfully.", safe=False)
                else:
                    return JsonResponse({"errors": measurementUnitSerializer.errors}, status=400)
            except MeasurementUnit.DoesNotExist:
                return JsonResponse("Measurement Unit not found.", safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'update'. Use PUT.")

    # Handle the 'delete' method
    elif method == 'delete':
        if request.method == 'DELETE':
            measurementUnitData = JSONParser().parse(request)
            measurementUnit_id = measurementUnitData.get('id', None)

            if measurementUnit_id is not None:
                try:
                    measurementUnit = MeasurementUnit.objects.get(id=measurementUnit_id)
                    measurementUnit.delete()

                    # Log the deletion
                    ActivityLog.objects.create(
                        user=request.user,
                        method='delete',
                        module='Configuration',
                        model='MeasurementUnit',
                        record_id=measurementUnit_id,
                        changes='Record Deleted'
                    )

                    # Reset the AUTO_INCREMENT in MySQL
                    with connection.cursor() as cursor:
                        cursor.execute("ALTER TABLE Configuration_measurementUnit AUTO_INCREMENT = 1;")

                    return JsonResponse("Measurement Unit deleted successfully. Next record will start at ID 1.", safe=False)
                except MeasurementUnit.DoesNotExist:
                    return JsonResponse("Measurement Unit not found.", safe=False)
            else:
                return JsonResponse("Missing 'id' in request body.", safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'delete'. Use DELETE.")

