from django.db import models

class MeasurementUnit(models.Model):
    measurement = [
        ('bit', 'Bit'),
        ('kilobit', 'Kilobit'),
        ('megabit', 'Megabit'),
        ('byte', 'Byte'),
        ('kilobyte', 'Kilobyte'),
        ('megabyte', 'Megabyte'),
    ]
    unit = models.CharField(choices=measurement, default='bit', max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.unit

class Label(models.Model):
    label = models.CharField(max_length=255, blank=False, null=False, unique=True)
    circuit = models.CharField(max_length=255, blank=False, null=False, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.label} - {self.circuit}"