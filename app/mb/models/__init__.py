""" mb.models initialized here. Importing all models from submodules here. """

from .base_model import (
    CustomQuerySet,
    ActiveManager,
    BaseModel)

from .unsorted import (
    AttributeRelation,
    ChoiceValue,
    ChoiceSetOptionRelation,
    EntityClass,
    RelationClass,
    FoodItem,
    MasterAttributeGroup,
    AttributeGroupRelation,
    MasterAttribute,
    MasterChoiceSetOption,
    MasterEntity,
    MasterReference,
    MasterUnit,
    SourceAttribute,
    SourceChoiceSetOption,
    SourceChoiceSetOptionValue,
    SourceEntity,
    SourceMeasurementValue,
    SourceMethod,
    SourceStatistic,
    SourceUnit,
    EntityRelation,
    SourceReference,
    ReferenceRelation,
    UnitConversion,
    UnitRelation,
    TimePeriod,
    DietSet,
    DietSetItem,
    ProximateAnalysis,
    ProximateAnalysisItem,
    ViewMasterTraitValue,
    ViewProximateAnalysisTable)

from .habitat_models import (
    SourceHabitat,
    MasterHabitat,
    HabitatRelation)

from .location_models import (
    SourceLocation,
    MasterLocation,
    LocationRelation)

from .occurrence_models import (
    Occurrence,
    Event)

from .validators import (
    validate_doi)
