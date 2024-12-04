from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.Configuration.models import Label
from apps.Configuration.serializers import LabelSerializer
from apps.ActivityLog.models import ActivityLog
from django.db import connection
import json

# @csrf_exempt
@login_required
@permission_classes([IsAuthenticated])
def labelApi(request, method=None, id=None):
    """
    API view to handle Label creation, listing, viewing, updating, and deletion.
    Only allows one Label record at a time. After a record is created, only updates 
    are allowed until the record is deleted. On deletion, ID resets to 1 for the next creation.

    Parameters:
    - request: The HTTP request object.
    - method: The action to perform ('create', 'list', 'view', 'update', 'delete').
    - id: The ID of the Label (not used directly as it's extracted from request data).

    Returns:
    - JsonResponse with the result of the operation or an error message.
    """

    if method not in ['create', 'list', 'view', 'update', 'delete']:
        return HttpResponseBadRequest("Invalid request method.")

    # Permission checks for different methods
    if method in ['list', 'view'] and not request.user.has_perm('Configuration.view_label'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'create' and not request.user.has_perm('Configuration.add_label'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'update' and not request.user.has_perm('Configuration.change_label'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    if method == 'delete' and not request.user.has_perm('Configuration.delete_label'):
        return JsonResponse("Permission denied.", status=403, safe=False)

    # Check if a record already exists before allowing 'create'        
    if method == 'create':
        if request.method == 'POST':
            # Parse request data
            labelData = JSONParser().parse(request)
            label_value = labelData.get('label')
            circuit_value = labelData.get('circuit')

            # Check if a Label with the same 'label' or 'circuit' exists
            existing_label = Label.objects.filter(label=label_value).exists()
            existing_circuit = Label.objects.filter(circuit=circuit_value).exists()

            if existing_label and existing_circuit:
                return JsonResponse("Both label and circuit names already exist.", status=400, safe=False)
            elif existing_label:
                return JsonResponse("Label name already exists.", status=400, safe=False)
            elif existing_circuit:
                return JsonResponse("Circuit name already exists.", status=400, safe=False)

            # If neither exist, proceed to save the new record
            labelSerializer = LabelSerializer(data=labelData)
            if labelSerializer.is_valid():
                # Save the new record
                label = labelSerializer.save()

                # Log the creation of the Label
                ActivityLog.objects.create(
                    user=request.user,
                    method='create',
                    module='Configuration',
                    model='Label',
                    record_id=label.id,
                    changes='New Record'
                )

                return JsonResponse("Label added successfully.", safe=False)
            else:
                return JsonResponse({"errors": labelSerializer.errors}, status=400)
        else:
            return HttpResponseBadRequest("Invalid request method for 'create'. Use POST.")

    # Handle the 'list' method
    elif method == 'list':
        if request.method == 'GET':
            labels = Label.objects.all()
            labelSerializer = LabelSerializer(labels, many=True)
            return JsonResponse(labelSerializer.data, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'list'. Use GET.")

    # Handle the 'view' method
    elif method == 'view':
        if request.method == 'GET':
            try:
                label_id = request.GET.get('id')  # Extract id from query parameters
                if not label_id:
                    return JsonResponse("Missing 'id' parameter.", status=400, safe=False)

                label = Label.objects.get(id=label_id)
                labelSerializer = LabelSerializer(label)
                return JsonResponse(labelSerializer.data, safe=False)
            except Label.DoesNotExist:
                return JsonResponse("Label not found.", safe=False)
            except Exception as e:
                return JsonResponse("An error occurred.", status=500, safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'view'. Use GET.")

    # Handle the 'update' method
    elif method == 'update':
        if request.method == 'PUT':
            labelData = JSONParser().parse(request)
            label_id = labelData.get('id', None)
            if not label_id:
                return JsonResponse("Missing 'id' in request body.", status=400, safe=False)

            try:
                label = Label.objects.get(id=label_id)

                # Serialize current data before update
                old_data = LabelSerializer(label).data

                labelSerializer = LabelSerializer(label, data=labelData, partial=True)
                if labelSerializer.is_valid():
                    labelSerializer.save()

                    # Serialize new data after update
                    new_data = LabelSerializer(label).data

                    # Compute changes
                    changes = {}
                    for field in labelData.keys():
                        old_value = old_data.get(field)
                        new_value = new_data.get(field)
                        if old_value != new_value:
                            changes[field] = {'from': old_value, 'to': new_value}

                    # Log the update
                    ActivityLog.objects.create(
                        user=request.user,
                        method='update',
                        module='Configuration',
                        model='Label',
                        record_id=label.id,
                        changes=changes
                    )

                    return JsonResponse("Label updated successfully.", safe=False)
                else:
                    return JsonResponse({"errors": labelSerializer.errors}, status=400)
            except Label.DoesNotExist:
                return JsonResponse("Label not found.", safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'update'. Use PUT.")

    # Handle the 'delete' method
    elif method == 'delete':
        if request.method == 'DELETE':
            labelData = JSONParser().parse(request)
            label_id = labelData.get('id', None)

            if label_id is not None:
                try:
                    label = Label.objects.get(id=label_id)
                    label.delete()

                    # Log the deletion
                    ActivityLog.objects.create(
                        user=request.user,
                        method='delete',
                        module='Configuration',
                        model='Label',
                        record_id=label_id,
                        changes='Record Deleted'
                    )

                    # Reset the AUTO_INCREMENT in MySQL
                    with connection.cursor() as cursor:
                        cursor.execute("ALTER TABLE Configuration_label AUTO_INCREMENT = 1;")

                    return JsonResponse("Label deleted successfully. Next record will start at ID 1.", safe=False)
                except Label.DoesNotExist:
                    return JsonResponse("Label not found.", safe=False)
            else:
                return JsonResponse("Missing 'id' in request body.", safe=False)
        else:
            return HttpResponseBadRequest("Invalid request method for 'delete'. Use DELETE.")

