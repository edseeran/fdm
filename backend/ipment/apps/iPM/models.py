from django.db import models

class Data(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    inbound_rate = models.DecimalField(max_digits=30, decimal_places=2, blank=False, null=True)
    outbound_rate = models.DecimalField(max_digits=30, decimal_places=2, blank=False, null=True)
    time = models.DateTimeField()
    
    def __str__(self):
        return self.name

class Dashboard(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    db_type = models.TextField(blank=True, null=True)
    data = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.description}"
    
# class Token(models.Model):
#     token = models.CharField(max_length=255, blank=False, null=False)
#     create_time = models.DateTimeField()
#     expiration = models.IntegerField()
    
    # command is: python manage.py refresh_token