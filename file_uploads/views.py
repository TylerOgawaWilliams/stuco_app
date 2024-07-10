from .models import UploadedFile
from .forms import UploadedFileForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView
import logging

LOGGER = logging.getLogger(__name__)


class IndexView(ListView):
    def __init__(self, *args, **kwargs):
        self.modal = kwargs.pop('modal', False)
        super().__init__(*args, **kwargs)

    model = UploadedFile
    template_name = 'file_uploads/index.html'
    context_object_name = 'files'
    modal = False

    def get_queryset(self):
        return UploadedFile.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # get the default context data
        context['modal'] = self.modal  # add extra field to the context
        return context


def _ensure_file_name(request, default_name=None):
    post_data = request.POST.copy()
    if not post_data.get('name'):
        if 'file' in request.FILES:
            post_data['name'] = request.FILES['file'].name
        elif 'files' in request.FILES:
            post_data['name'] = request.FILES.getlist('files')[0].name
        elif 'file_name_from_user' in request.POST:
            post_data['name'] = request.POST['file_name_from_user']
        elif default_name:
            post_data['name'] = default_name

        request.POST = post_data
    return request.POST


def file_upload_modal(request, max_files=5, min_files=1):
    return file_upload(
        request,
        max_files=max_files,
        min_files=min_files,
        modal=True
    )


def file_upload(request, max_files=5, min_files=1, modal=False):
    if request.method == 'POST':

        form = UploadedFileForm(request.POST, request.FILES, max_files=max_files, min_files=min_files)
        if form.is_valid():
            form.save(commit=False)
            next_file_number = 0
            for next_file in request.FILES.getlist('files'):
                next_file_number += 1
                next_uploaded_file = UploadedFile(
                    file=next_file,
                    name=next_file.name.split('/')[-1],
                    description=(
                        f"{form.cleaned_data['description'] if form.cleaned_data['description'] else 'N/A'}"
                        f"-{next_file_number}"
                    ),
                    created_by=request.user.username
                )
                next_uploaded_file.save()
            if modal:
                return HttpResponse(status=200, headers={'HX-Trigger': 'fileListChanged'})

            return redirect('list_files')
        else:
            return render(request, 'file_uploads/upload_file_form.html', {'form': form, 'modal': modal})

    # This is a Get Request - initial load of form . . .
    form = UploadedFileForm(max_files=max_files, min_files=min_files)
    return render(request, 'file_uploads/upload_file_form.html', {'form': form, 'modal': modal})


def edit(request, pk, template_name='file_uploads/edit.html'):
    uploaded_file = get_object_or_404(UploadedFile, pk=pk)
    if request.method == 'POST':
        # If user chose to not enter a name, use the file name
        request.POST = _ensure_file_name(request, default_name=uploaded_file.file.name.split('/')[-1])

        form = UploadedFileForm(request.POST, instance=uploaded_file)

        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.name = (
                request.POST['file_name_from_user'] if request.POST['file_name_from_user']
                else uploaded_file.file.name.split('/')[-1]
            )
            uploaded_file.save()
            return redirect('list_files')
        else:
            LOGGER.error(f"form is not valid: {form.errors}")
    else:
        form = UploadedFileForm(instance=uploaded_file)

    return render(
        request,
        template_name,
        {
            'form': form,
            'uploaded_file_name_from_user': uploaded_file.name,
            'uploaded_file_internal_file_name': uploaded_file.file.name.split('/')[-1],
        }
    )


def delete(request, pk, template_name='file_uploads/confirm_delete.html'):
    uploaded_file = get_object_or_404(UploadedFile, pk=pk)
    if request.method == 'POST':
        uploaded_file.delete()
        return redirect('list_files')
    return render(request, template_name, {'object': uploaded_file})


def demo(request, template_name='file_uploads/demo_uploads.html'):
    return render(request, template_name, {})
