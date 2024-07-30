from django.db import models

# Create your models here.


class Report(models.Model):
    report_name = models.CharField(max_length=255)
    data_name = models.CharField(max_length=255)
    data = models.JSONField(default="")

    class Meta:
        db_table = "report_data"
