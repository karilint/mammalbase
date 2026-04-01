import os
from pathlib import PurePath

from django import forms
from django.conf import settings

from .models import SourceDocument


class SourceDocumentUploadForm(forms.ModelForm):
    class Meta:
        model = SourceDocument
        fields = ['pdf_file', 'title', 'authors', 'year', 'doi']

    def clean_pdf_file(self):
        pdf_file = self.cleaned_data['pdf_file']

        original_name = pdf_file.name or ''
        if not original_name:
            raise forms.ValidationError('Uploaded file must have a filename.')

        path_parts = PurePath(original_name).parts
        if '..' in path_parts:
            raise forms.ValidationError('Invalid filename: path traversal is not allowed.')

        safe_name = os.path.basename(original_name)
        if safe_name in {'', '.', '..'}:
            raise forms.ValidationError('Invalid filename for uploaded PDF.')

        pdf_file.name = safe_name

        max_pdf_mb = getattr(settings, 'RECODE_MAX_PDF_MB', 25)
        max_pdf_size = max_pdf_mb * 1024 * 1024
        if pdf_file.size > max_pdf_size:
            raise forms.ValidationError(f'PDF exceeds maximum allowed size of {max_pdf_mb} MB.')

        header = pdf_file.read(5)
        pdf_file.seek(0)
        if header != b'%PDF-':
            raise forms.ValidationError('Uploaded file is not a valid PDF (missing %PDF- signature).')

        if not safe_name.lower().endswith('.pdf'):
            raise forms.ValidationError('Please upload a PDF file.')

        return pdf_file
