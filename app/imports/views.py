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
from .importers.proximate_analysis_importer import ProximateAnalysisImporter
from .validation_lib.occurrence_validation import Occurrence_validation
from .validation_lib.diet_set_validation import Diet_set_validation
from .validation_lib.ets_validation import Ets_validation
from .validation_lib.proximate_analysis_validation import Proximate_analysis_validation
from .views_wrapper import wrapper


@login_required
def import_diet_set(request):
	"""Import diet set from web form.

	Args:
		request (_type_): _description_

	Returns:
		HTTP-response: html-template
	"""
	validator = Diet_set_validation()
	importer = DietImporter()
	path = "import_diet_set"

	return wrapper(request, validator, importer, path)

@login_required
def import_proximate_analysis(request):
	"""Import proximate analysis from web form.

	Args:
		request (_type_): _description_

	Returns:
		HTTP-response: html-template
	"""
	validator = Proximate_analysis_validation()
	importer = ProximateAnalysisImporter()
	path = "import_proximate_analysis"

	return wrapper(request, validator, importer, path)

@login_required
def import_ets(request):
	"""Import ets from web form.

	Args:
		request (_type_): _description_

	Returns:
		HTTP-response: html-template
	"""
	validator = Ets_validation()
	importer = EtsImporter()
	path = "import_ets"

	return wrapper(request, validator, importer, path)


@login_required
def import_occurrences(request):
	"""Import occurrences from web form.

	Args:
		request (_type_): _description_

	Returns:
		HTTP-response: html-template
	"""
	validator = Occurrence_validation()
	importer = OccurrencesImporter()
	path = "import_occurrences"

	return wrapper(request, validator, importer, path)


	


