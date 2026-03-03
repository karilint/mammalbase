from django import forms

from .models import SourceDocument


class SourceDocumentUploadForm(forms.ModelForm):
    class Meta:
        model = SourceDocument
        fields = ['pdf_file', 'title', 'authors', 'year', 'doi']

    def clean_pdf_file(self):
        pdf_file = self.cleaned_data['pdf_file']
        if not pdf_file.name.lower().endswith('.pdf'):
            raise forms.ValidationError('Please upload a PDF file.')
        return pdf_file
