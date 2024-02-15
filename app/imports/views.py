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
from .validation_lib.diet_set_validation import Diet_set_validation
from .validation_lib.ets_validation import Ets_validation
#from .validation_lib.proximate_analysis import Proximate_analysis_validation
from .views_wrapper import wrapper




@login_required
def import_diet_set(request):
	validator = Diet_set_validation()
	importer = DietImporter()
	path = "import_diet_set"

	return wrapper(request, validator, importer, path)

@login_required
def import_proximate_analysis(request):
	#validator = Proximate_analysis_validation()
	#importer = ProximateAnalysisImporter()
	path = "import_proximate_analysis"

	#return wrapper(request, validator, importer, path)
	

@login_required
def import_ets(request):
	validator = Ets_validation()
	importer = EtsImporter()
	path = "import_ets"

	return wrapper(request, validator, importer, path)


@login_required
def import_occurrences(request):
	validator = Occurrence_validation()
	importer = OccurrencesImporter()
	path = "import_occurrences"

	return wrapper(request, validator, importer, path)


	


