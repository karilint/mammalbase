class ExportFileWriter:

    def __init__(self):
        self.files = []


    def save_zip_to_django_model(self, export_file_id: int):
        pass


    def zip(self, tsv_files):
        pass


    def write_rows(self, file_path, *rows):
        self.files.append((file_path, rows))
