import csv
import zipfile
from datetime import datetime
from zipfile import ZipFile

from django.core.files import File
from exports.models import ExportFile

class ExportFileWriter:

    def __init__(self):
        self.zip_file_path = f'MammalBase_export_{datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f")}.zip'
        self.temp_zip_writer = ZipFile(self.zip_file_path, 'w', compression=zipfile.ZIP_DEFLATED)


    def save_zip_to_django_model(self, export_file_id: int):
        with open(self.zip_file_path, 'rb') as zip_file:
            export_file = ExportFile.objects.get(pk=export_file_id)
            export_file.file = File(zip_file)
            export_file.save()
            zip_file.close()


    def zip(self, tsv_files):
        for tsv_file in tsv_files:
            self.temp_zip_writer.write(tsv_file)
        self.temp_zip_writer.close()


    def write_rows(self, file_path, *rows):
        f = open(file_path, 'w')
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(rows)
        f.close()

