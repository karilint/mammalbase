import logging
import pandas as pd

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

from utils.views import render	# MB Utils
from .tools import messages, create_proximate_analysis
from .checker import Check
from .importers.diet_importer import DietImporter
from .importers.ets_importer import EtsImporter
from .importers.occurrence_importer import OccurrencesImporter
from .validation_lib.occurrence_validation import Occurrence_validation




@login_required
def import_diet_set(request):
	if request.method == "GET":
		return render(request, "import/import_diet_set.html")
	try:
		file = request.FILES["csv_file"]
		df = pd.read_csv(file, sep='\t')
		check = Check(request)
		force = "force" in request.POST

		if not check.check_valid_author(df) or not check.check_all_ds(df, force):
			return HttpResponseRedirect(reverse("import_diet_set"))

		importer = DietImporter()
		for row in df.itertuples():
			importer.importRow(row)

		success_message = "File imported successfully. "+ str(df.shape[0])+ " rows of data was imported."
		messages.add_message(request, 50 ,success_message, extra_tags="import-message")
		messages.add_message(request, 50 , df.to_html(), extra_tags="show-data")
		return HttpResponseRedirect(reverse("import_diet_set"))

	except Exception as e:
		messages.error(request,"Unable to upload file. "+repr(e))
	return HttpResponseRedirect(reverse("import_diet_set"))

@login_required
def import_proximate_analysis(request):
	if request.method == "GET":
		return render(request, "import/import_proximate_analysis.html")
	try:
		
		file = request.FILES["csv_file"]
		df = pd.read_csv(file, sep='\t')
		check = Check(request)
		force = "force" in request.POST

		if not check.check_valid_author(df) or not check.check_all_pa(df, force):
			return HttpResponseRedirect(reverse("import_proximate_analysis"))

		for row in df.itertuples():
			create_proximate_analysis(row, df)

		success_message = "File imported successfully. "+ str(df.shape[0])+ " rows of data was imported."
		messages.add_message(request, 50 ,success_message, extra_tags="import-message")
		messages.add_message(request, 50 , df.to_html(), extra_tags="show-data")
		return HttpResponseRedirect(reverse("import_proximate_analysis"))

	except Exception as e:
		logging.getLogger("error_logger").error("Unable to upload file. "+repr(e))
		messages.error(request,"Unable to upload file. "+repr(e))
	return HttpResponseRedirect(reverse("import_proximate_analysis"))
	

@login_required
def import_ets(request):
	if request.method == "GET":
		return render(request, "import/import_ets.html")
	try:
		csv_file = request.FILES["csv_file"]
		df = pd.read_csv(csv_file, sep='\t')
		check = Check(request)

		
		if not check.check_valid_author(df) or not check.check_all_ets(df):
			return HttpResponseRedirect(reverse("import_ets"))

		importer = EtsImporter()
  
		for row in df.itertuples():
			importer.importRow(row)
		success_message = "File imported successfully. "+ str(df.shape[0])+ " rows of data was imported."
		messages.add_message(request, 50 ,success_message, extra_tags="import-message")
		messages.add_message(request, 50 , df.to_html(), extra_tags="show-data")
		return HttpResponseRedirect(reverse("import_ets"))

	except Exception as e:
		messages.error(request,"Unable to upload file. "+repr(e))
	return HttpResponseRedirect(reverse("import_ets"))


@login_required
def import_occurrences(request):
	if request.method == "GET":
		return render(request, "import/import_occurrences.html")
	
	validator = Occurrence_validation()
	importer = OccurrencesImporter()

	try:
		csv_file = request.FILES["csv_file"]
		df = pd.read_csv(csv_file, sep='\t')

		importing_errors = []
		success_rows = 0
		message = None

		headers =  list(df.columns.values)
		data = validator.data

		for row in df.itertuples(index=False):
			# Loop through headers and add the data to empty data dict for validation
			for i, x in enumerate(row):
				data[headers[i]] = x
			print("Data saatu rivistä ja lisätty se data dictiin, seuraavana validointi riville !")

			# Check through the data and the rules that they are valid
			isvalid = validator.is_valid(data, validator.rules)
			errors = validator.errors
			print(str(errors))
			#If data is not valid return the reason
			if not isvalid:
				messages.error(request,"Unable to upload file. "+ str(errors))
				return HttpResponseRedirect(reverse("import_occurrences"))
			
			# if data is valid, import it to database
			print("SEURAAVANA IMPORTTTAAAAUS")
			created = importer.importRow(row, importing_errors)
			created
			print(str(success_rows))
			if created:
				success_rows += 1
				print(print("JEEE RIVI IMPORTATTU"))
				
			else:
				print("FAILAUKSEEEN")
		if success_rows == 0:
			message = "0 rows of data was imported"
		elif len(importing_errors) > 0 and success_rows > 0:
			message = str(success_rows) + " rows of data was imported successfully with some errors in these rows: "

			for error in importing_errors:
				message = message + error
		else:
			message = "File imported successfully. "+ str(df.shape[0])+ " rows of data was imported."
		messages.add_message(request, 50 ,message, extra_tags="import-message")
		messages.add_message(request, 50 , df.to_html(), extra_tags="show-data")
		return HttpResponseRedirect(reverse("import_occurrences"))

	except Exception as e:
		logging.getLogger("error_logger").error("Unable to upload file due coding error. "+repr(e))
		messages.error(request,"Unable to upload file. "+repr(e))
	return HttpResponseRedirect(reverse("import_occurrences"))


