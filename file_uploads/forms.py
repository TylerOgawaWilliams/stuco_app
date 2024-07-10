from django import forms
from .models import UploadedFile
from .multi_upload_util import MultipleFileField
import logging

LOGGER = logging.getLogger(__name__)

MAX_FILE_SIZE = 1024 * 1024 * 5


class UploadedFileForm(forms.ModelForm):
    # Default to 1 file upload
    files = MultipleFileField(
        min_num=1,
        max_num=1,
        max_file_size=MAX_FILE_SIZE,
        label="File",
    )

    def __init__(self, *args, **kwargs):
        _multiple = False
        _max_files = 0
        _min_files = 0
        if "max_files" in kwargs:
            _max_files = int(kwargs.pop("max_files"))
        else: # Default to 1 file upload
            _max_files = 1

        if "min_files" in kwargs:
            _min_files = int(kwargs.pop("min_files"))
            if _min_files < 0 or _min_files > _max_files:
                raise ValueError("min_files must be between 0 and max_files")
        else:
            _min_files = 1

        _multiple = (_max_files != 1)
        _required = (_min_files > 0)

        super().__init__(*args, **kwargs)
        self.fields['files'] = MultipleFileField(
            min_num=_min_files,
            max_num=_max_files,
            max_file_size=MAX_FILE_SIZE,
            label="File" if _max_files < 2 else "Files",
            attrs={
                "required": _required,
                "multiple": "multiple" if _multiple else "",
            },
            required=_required
        )

    class Meta:
        model = UploadedFile
        fields = ["files", "description"]
