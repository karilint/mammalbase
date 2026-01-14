# Test import corrections

This inventory lists outdated imports in `app/tests/` and their corrected targets.

## Model imports

- `from app.models import Observation, Location, Species`
  - Use: `from mb.models import Occurrence, SourceLocation, SourceEntity` (or update tests to the current mb models)
- `from app.models import Project, Location, Survey, Deployment, Camera, MediaFile`
  - Use: `from mb.models import ProximateAnalysis` (proximate analysis importers no longer use project/location models)
- `from app.models import Collection, CollectionAttribute, ChoiceValue`
  - Use: `from mb.models import ChoiceValue`
- `from exports.models import Export`
  - Use: `from exports.models import ExportFile`
- `from catalogue.models import Taxon, ChoiceValue`
  - Use: `from tdwg.models import Taxon`

## Utility module imports

- `from imports.base_importer import BaseImporter`
  - Use: `from imports.importers.base_importer import BaseImporter`
- `from imports.occurrence_import import OccurrenceImporter`
  - Use: `from imports.importers.occurrence_importer import OccurrencesImporter`
- `from imports.pa_import import PAImporter`
  - Use: `from imports.importers.proximate_analysis_importer import ProximateAnalysisImporter`
- `from imports.validation import ImportValidator`
  - Use: `from imports.validation_lib.base_validation import Validation`
