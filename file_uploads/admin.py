from django.contrib import admin
from .models import UploadedFile


# Register your models here.
@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
    )

    readonly_fields = (
        "created_at",
        "created_by",
        "last_updated_at",
        "last_updated_by",
    )
