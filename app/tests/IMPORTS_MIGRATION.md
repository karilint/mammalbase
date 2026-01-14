# Test import corrections

This inventory lists outdated imports in `app/tests/` and their corrected targets.

## Model imports

- `from app.models import Observation, Location, Species`
  - Use: `from mb.models import Observation, Location, Species`
- `from app.models import Project, Location, Survey, Deployment, Camera, MediaFile`
  - Use: `from mb.models import Project, Location, Survey, Deployment, Camera, MediaFile`
- `from app.models import Collection, CollectionAttribute, ChoiceValue`
  - Use: `from mb.models import Collection, CollectionAttribute, ChoiceValue`
- `from exports.models import Export`
  - Use: `from exports.models import ExportFile`
- `from catalogue.models import Taxon, ChoiceValue`
  - Use: `from tdwg.models import Taxon, ChoiceValue`

## Utility module imports

- `from imports.base_importer import BaseImporter`
  - Use: `from imports.base_importer import BaseImporter`
- `from imports.occurrence_import import OccurrenceImporter`
  - Use: `from imports.occurrence_import import OccurrenceImporter`
