from django import forms
from django.core.exceptions import ValidationError
import logging

LOGGER = logging.getLogger(__name__)
MAX_FILE_SIZE = 1024 * 1024 * 5


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, *args, **kwargs):
        self.multiple = kwargs.pop('multiple', True)
        self.allow_multiple_selected = self.multiple
        self.required = kwargs.pop('required', False)

        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        if not attrs:
            attrs = {}

        if self.multiple:
            attrs['multiple'] = 'multiple'

        if self.required:
            attrs['required'] = self.required

        return super().render(name, value, attrs, renderer)


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        self.min_num = kwargs.pop('min_num', 0)
        self.max_num = kwargs.pop('max_num', 10)
        self.maximum_file_size = kwargs.pop('max_file_size', MAX_FILE_SIZE)
        self.multiple = self.max_num is None or self.max_num > 1
        my_attrs = kwargs.pop('attrs', {})
        my_attrs['multiple'] = self.multiple
        my_attrs['required'] = self.min_num > 0

        self.widget = MultipleFileInput(
            attrs=my_attrs,
        )

        if self.min_num == 0:
            kwargs['required'] = False
        else:
            kwargs['required'] = True

        super().__init__(*args, **kwargs)

    @property
    def get_multiple(self):
        return self.multiple

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]

        for next_result in result:
            if next_result.size > self.maximum_file_size:
                raise ValidationError(f"File size must be less than {self.maximum_file_size} bytes")

        return result
