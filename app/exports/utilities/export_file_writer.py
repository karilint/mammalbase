""" Helper class that handled tsv file writing and folder zipping """
from csv import writer as csv_writer
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED

from django.core.files import File

from exports.models import ExportFile

class ExportFileWriter:
    """ Writes files, zips and adds as File object to the ExportFile model """
    def __init__(self):
        self.zip_file_path = (
                'MammalBase_export_'
                f'{datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f")}.zip')


    def save_zip_to_django_model(self, export_file_id: int):
        """ Creates Django File object and saves it to the Model """
        with open(self.zip_file_path, 'rb') as zip_file:
            export_file = ExportFile.objects.get(pk=export_file_id)
            export_file.file = File(zip_file)
            export_file.save()
            zip_file.close()


    def zip(self, tsv_files):
        """ Zips files in list to zip archive """
        temp_zip_writer = ZipFile(
                self.zip_file_path, 'w',
                compression=ZIP_DEFLATED)
        for tsv_file in tsv_files:
            temp_zip_writer.write(tsv_file)
        temp_zip_writer.close()


    def write_rows(self, file_path, headers, rows):
        """ Writes header and rows to file """
        f = open(file_path, 'w')
        writer = csv_writer(f, delimiter='\t', lineterminator='\n')
        writer.writerow(headers)
        writer.writerows(rows)
        f.close()
