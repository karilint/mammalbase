```mermaid
classDiagram
	Occurrence -->Event
	Occurrence -->Location
	Occurrence -->Taxon
	AttributeRelation -->SourceAttribute
	AttributeRelation -->MasterAttribute
	AttributeGroupRelation -->MasterAttributeGroup
	AttributeGroupRelation -->MasterAttribute
	ChoiceSetOptionRelation -->SourceChoiceSetOption
	ChoiceSetOptionRelation -->MasterChoiceSetOption
	DietSet -->SourceReference
	DietSet -->SourceEntity
	DietSet -->SourceLocation
	DietSet -->ChoiceValue
	DietSet -->TimePeriod
	DietSet -->SourceMethod
	DietSetItem -->DietSet
	DietSetItem -->FoodItem
	EntityRelation -->RelationClass
	EntityRelation -->SourceEntity
	EntityRelation -->MasterEntity
	EntityRelation -->MasterChoiceSetOption
	EntityRelation -->MasterChoiceSetOption
	FoodItem -->ChoiceValue
	FoodItem -->TaxonomicUnits
	FoodItem -->TaxonomicUnits
	MasterAttribute -->MasterReference
	MasterAttribute -->EntityClass
	MasterAttribute -->MasterUnit
	MasterChoiceSetOption -->MasterAttribute
	MasterEntity -->MasterReference
	MasterEntity -->EntityClass
	MasterEntity -->Taxon
	MasterLocation -->MasterReference
	MasterUnit -->SourceUnit
	ProximateAnalysis -->SourceReference
	ProximateAnalysis -->SourceLocation
	ProximateAnalysis -->SourceMethod
	ProximateAnalysisItem -->ProximateAnalysis
	ProximateAnalysisItem -->FoodItem
	ProximateAnalysisItem -->SourceLocation
	SourceAttribute -->SourceReference
	SourceAttribute -->EntityClass
	SourceAttribute -->MasterAttribute
	SourceAttribute -->SourceMethod
	SourceChoiceSetOption -->SourceAttribute
	SourceChoiceSetOptionValue -->SourceEntity
	SourceChoiceSetOptionValue -->SourceChoiceSetOption
	SourceEntity -->SourceReference
	SourceEntity -->EntityClass
	SourceLocation -->SourceReference
	SourceMeasurementValue -->SourceEntity
	SourceMeasurementValue -->SourceAttribute
	SourceMeasurementValue -->SourceLocation
	SourceMeasurementValue -->SourceStatistic
	SourceMeasurementValue -->SourceUnit
	SourceMeasurementValue -->ChoiceValue
	SourceMeasurementValue -->ChoiceValue
	SourceMethod -->SourceReference
	SourceReference -->MasterReference
	SourceStatistic -->SourceReference
	TaxonomicUnits -->Kingdom
	TaxonomicUnits -->TaxonUnitTypes 
	TaxonomicUnits -->SynonymLinks
	UnitConversion -->MasterUnit
	UnitRelation -->MasterUnit
	UnitRelation -->SourceUnit
	TimePeriod -->SourceReference
	ViewMasterTraitValue: -->MasterEntity
	ViewMasterTraitValue: -->MasterAttribute
	ViewProximateAnalysisTable: -->TaxonomicUnits
	AttributeRelation: +FK  source_attribute
	AttributeRelation: +FK  master_attribute
	AttributeRelation: +String  remarks
	AttributeRelation: +get_absolute_url()
	AttributeRelation: +__str__()
	ChoiceValue: +String  choice_set
	ChoiceValue: +String  caption
	ChoiceValue: +get_absolute_url()
	ChoiceValue: +__str__()
	ChoiceSetOptionRelation: +FK  source_choiceset_option
	ChoiceSetOptionRelation: +FK  master_choiceset_option
	ChoiceSetOptionRelation: +String  remarks
	ChoiceSetOptionRelation: +get_absolute_url()
	ChoiceSetOptionRelation: +__str__()
	EntityClass: +String  name
	EntityClass: +get_absolute_url()
	EntityClass: +__str__()
	RelationClass: +String  name
	RelationClass: +get_absolute_url()
	RelationClass: +__str__()
	FoodItem: +String  name
	FoodItem: +FK  part
	FoodItem: +FK  tsn
	FoodItem: +FK  pa_tsn
	FoodItem: +Boolean  is_cultivar
	FoodItem: +get_absolute_url()
	FoodItem: +__str__()
	MasterAttributeGroup: +String  name
	MasterAttributeGroup: +String  remarks
	MasterAttributeGroup: +__str__()
	AttributeGroupRelation: +FK  group
	AttributeGroupRelation: +FK  attribute
	AttributeGroupRelation: +int  display_order
	AttributeGroupRelation: +__str__()
	MasterAttribute: +FK  reference
	MasterAttribute: +FK  entity
	MasterAttribute: +FK  source_attribute
	MasterAttribute: +String  name
	MasterAttribute: +FK  unit
	MasterAttribute: +String  min_allowed_value
	MasterAttribute: +String  max_allowed_value
	MasterAttribute: +String  description
	MasterAttribute: +String  remarks
	MasterAttribute: +FK  groups
	MasterAttribute: +String  value_type
	MasterAttribute: +get_absolute_url()
	MasterAttribute: +__str__()
	MasterChoiceSetOption: +FK  master_attribute
	MasterChoiceSetOption: +int  display_order
	MasterChoiceSetOption: +String  name
	MasterChoiceSetOption: +String  description
	MasterChoiceSetOption: +get_absolute_url()
	MasterChoiceSetOption: +__str__()
	MasterEntity: +FK  reference
	MasterEntity: +FK  entity
	MasterEntity: +FK  source_entity
	MasterEntity: +String  name
	MasterEntity: +FK  taxon
	MasterEntity: +get_absolute_url()
	MasterEntity: +__str__()
	MasterLocation: +FK  reference
	MasterLocation: +String  name
	MasterLocation: +int  tgn
	MasterLocation: +get_absolute_url()
	MasterLocation: +__str__()
	MasterReference: +String  type
	MasterReference: +String  doi
	MasterReference: +URL  uri
	MasterReference: +String  first_author
	MasterReference: +int  year
	MasterReference: +String  title
	MasterReference: +String  container_title
	MasterReference: +int  volume
	MasterReference: +String  issue
	MasterReference: +String  page
	MasterReference: +String  citation
	MasterReference: +get_absolute_url()
	MasterReference: +__str__()
	MasterUnit: +String  name
	MasterUnit: +String  print_name
	MasterUnit: +String  quantity_type
	MasterUnit: +decimal  unit_value
	MasterUnit: +String  remarks
	MasterUnit: +get_absolute_url()
	MasterUnit: +__str__()
	SourceAttribute: +FK  reference
	SourceAttribute: +FK  entity
	SourceAttribute: +FK  master_attribute
	SourceAttribute: +String  name
	SourceAttribute: +int  type
	SourceAttribute: +String  remarks
	SourceAttribute: +FK  method
	SourceAttribute: +get_absolute_url()
	SourceAttribute: +__str__()
	SourceChoiceSetOption: +FK  source_attribute
	SourceChoiceSetOption: +int  display_order
	SourceChoiceSetOption: +String  name
	SourceChoiceSetOption: +String  description
	SourceChoiceSetOption: +get_absolute_url()
	SourceChoiceSetOption: +__str__()
	SourceChoiceSetOptionValue: +FK  source_entity
	SourceChoiceSetOptionValue: +FK  source_choiceset_option
	SourceChoiceSetOptionValue: +get_absolute_url()
	SourceChoiceSetOptionValue: +__str__()
	SourceEntity: +FK  reference
	SourceEntity: +FK  entity
	SourceEntity: +FK  master_entity
	SourceEntity: +String  name
	SourceEntity: +get_absolute_url()
	SourceEntity: +__str__()
	SourceLocation: +FK  reference
	SourceLocation: +String  name
	SourceLocation: +get_absolute_url()
	SourceLocation: +__str__()
	SourceMeasurementValue: +FK  source_entity
	SourceMeasurementValue: +FK  source_attribute
	SourceMeasurementValue: +FK  source_location
	SourceMeasurementValue: +int  n_total
	SourceMeasurementValue: +int  n_unknown
	SourceMeasurementValue: +int  n_male
	SourceMeasurementValue: +int  n_female
	SourceMeasurementValue: +decimal  minimum
	SourceMeasurementValue: +decimal  maximum
	SourceMeasurementValue: +decimal  mean
	SourceMeasurementValue: +decimal  std
	SourceMeasurementValue: +FK  source_statistic
	SourceMeasurementValue: +FK  source_unit
	SourceMeasurementValue: +FK  gender
	SourceMeasurementValue: +FK  life_stage
	SourceMeasurementValue: +String  measurement_accuracy
	SourceMeasurementValue: +String  measured_by
	SourceMeasurementValue: +String  remarks
	SourceMeasurementValue: +String  cited_reference
	SourceMeasurementValue: +String  unit
	SourceMeasurementValue: +clean()
	SourceMeasurementValue: +get_absolute_url()
	SourceMeasurementValue: +__str__()
	SourceMethod: +FK  reference
	SourceMethod: +String  name
	SourceMethod: +get_absolute_url()
	SourceMethod: +__str__()
	SourceStatistic: +FK  reference
	SourceStatistic: +String  name
	SourceStatistic: +get_absolute_url()
	SourceStatistic: +__str__()
	SourceUnit: +FK  master_unit
	SourceUnit: +String  name
	SourceUnit: +String  remarks
	SourceUnit: +get_absolute_url()
	SourceUnit: +__str__()
	EntityRelation: +FK  source_entity
	EntityRelation: +FK  master_entity
	EntityRelation: +FK  relation
	EntityRelation: +FK  relation_status
	EntityRelation: +FK  data_status
	EntityRelation: +String  remarks
	EntityRelation: +get_absolute_url()
	EntityRelation: +__str__()
	SourceReference: +String  citation
	SourceReference: +FK  master_reference
	SourceReference: +int  status
	SourceReference: +String  doi
	SourceReference: +get_absolute_url()
	SourceReference: +__str__()
	ReferenceRelation: +FK  source_reference
	ReferenceRelation: +FK  master_reference
	ReferenceRelation: +FK  relation
	ReferenceRelation: +get_absolute_url()
	ReferenceRelation: +__str__()
	UnitConversion: +FK  from_unit
	UnitConversion: +FK  to_unit
	UnitConversion: +decimal  coefficient
	UnitConversion: +get_absolute_url()
	UnitConversion: +__str__()
	UnitRelation: +FK  source_unit
	UnitRelation: +FK  master_unit
	UnitRelation: +String  remarks
	UnitRelation: +get_absolute_url()
	UnitRelation: +__str__()
	TimePeriod: +FK  reference
	TimePeriod: +String  name
	TimePeriod: +int  time_in_months
	TimePeriod: +get_absolute_url()
	TimePeriod: +__str__()
	DietSet: +FK  reference
	DietSet: +FK  taxon
	DietSet: +FK  location
	DietSet: +FK  gender
	DietSet: +int  sample_size
	DietSet: +String  cited_reference
	DietSet: +FK  time_period
	DietSet: +FK  method
	DietSet: +String  study_time
	DietSet: +get_absolute_url()
	DietSet: +__str__()
	DietSetItem: +FK  diet_set
	DietSetItem: +FK  food_item
	DietSetItem: +int  list_order
	DietSetItem: +decimal  percentage
	DietSetItem: +clean()
	DietSetItem: +get_absolute_url()
	DietSetItem: +__str__()
	ProximateAnalysis: +FK  reference
	ProximateAnalysis: +FK  location
	ProximateAnalysis: +String  cited_reference
	ProximateAnalysis: +FK  method
	ProximateAnalysis: +String  study_time
	ProximateAnalysis: +get_absolute_url()
	ProximateAnalysis: +__str__()
	ProximateAnalysisItem: +FK  proximate_analysis
	ProximateAnalysisItem: +FK  forage
	ProximateAnalysisItem: +FK  location
	ProximateAnalysisItem: +String  cited_reference
	ProximateAnalysisItem: +int  sample_size
	ProximateAnalysisItem: +decimal  dm_reported
	ProximateAnalysisItem: +decimal  moisture_reported
	ProximateAnalysisItem: +decimal  cp_reported
	ProximateAnalysisItem: +decimal  ee_reported
	ProximateAnalysisItem: +decimal  cf_reported
	ProximateAnalysisItem: +decimal  ash_reported
	ProximateAnalysisItem: +decimal  nfe_reported
	ProximateAnalysisItem: +decimal  total_carbohydrates_reported
	ProximateAnalysisItem: +decimal  cp_std
	ProximateAnalysisItem: +decimal  ee_std
	ProximateAnalysisItem: +decimal  cf_std
	ProximateAnalysisItem: +decimal  ash_std
	ProximateAnalysisItem: +decimal  nfe_std
	ProximateAnalysisItem: +String  transformation
	ProximateAnalysisItem: +String  remarks
	ProximateAnalysisItem: +String  measurement_determined_by
	ProximateAnalysisItem: +String  measurement_remarks
	ProximateAnalysisItem: +decimal  moisture_dispersion
	ProximateAnalysisItem: +String  moisture_measurement_method
	ProximateAnalysisItem: +decimal  dm_dispersion
	ProximateAnalysisItem: +String  dm_measurement_method
	ProximateAnalysisItem: +decimal  ee_dispersion
	ProximateAnalysisItem: +String  ee_measurement_method
	ProximateAnalysisItem: +decimal  cp_dispersion
	ProximateAnalysisItem: +String  cp_measurement_method
	ProximateAnalysisItem: +decimal  cf_dispersion
	ProximateAnalysisItem: +String  cf_measurement_method
	ProximateAnalysisItem: +decimal  ash_dispersion
	ProximateAnalysisItem: +String  ash_measurement_method
	ProximateAnalysisItem: +decimal  nfe_dispersion
	ProximateAnalysisItem: +String  nfe_measurement_method
	ProximateAnalysisItem: +get_absolute_url()
	ProximateAnalysisItem: +__str__()
	ViewMasterTraitValue: +PK  id
	ViewMasterTraitValue: +FK  master_id
	ViewMasterTraitValue: +String  master_entity_name
	ViewMasterTraitValue: +FK  master_attribute_id
	ViewMasterTraitValue: +String  master_attribute_name
	ViewMasterTraitValue: +String  traits_references
	ViewMasterTraitValue: +String  assigned_values
	ViewMasterTraitValue: +int  n_distinct_value
	ViewMasterTraitValue: +int  n_value
	ViewMasterTraitValue: +int  n_supporting_value
	ViewMasterTraitValue: +String  trait_values
	ViewMasterTraitValue: +String  trait_selected
	ViewMasterTraitValue: +String  trait_references
	ViewMasterTraitValue: +decimal  value_percentage
	ViewMasterTraitValue: +get_absolute_url()
	ViewMasterTraitValue: +__str__()
	ViewProximateAnalysisTable: +PK  id
	ViewProximateAnalysisTable: +FK  tsn
	ViewProximateAnalysisTable: +String  part
	ViewProximateAnalysisTable: +decimal  cp_std
	ViewProximateAnalysisTable: +decimal  ee_std
	ViewProximateAnalysisTable: +decimal  cf_std
	ViewProximateAnalysisTable: +decimal  ash_std
	ViewProximateAnalysisTable: +decimal  nfe_std
	ViewProximateAnalysisTable: +String  reference_ids
	ViewProximateAnalysisTable: +int  n_taxa
	ViewProximateAnalysisTable: +int  n_reference
	ViewProximateAnalysisTable: +int  n_analysis
	ViewProximateAnalysisTable: +get_absolute_url()
	ViewProximateAnalysisTable: +__str__()
	Taxon:+String  scientific_name
	Taxon:+String  taxon_id
	Taxon:+String  kingdom
	Taxon:+String  phylum
	Taxon:+String  class_name
	Taxon:+String  order
	Taxon:+String  suborder
	Taxon:+String  infraorder
	Taxon:+String  superfamily
	Taxon:+String  family
	Taxon:+String  subfamily
	Taxon:+String  tribe
	Taxon:+String  infrageneric_epithet
	Taxon:+String  genus
	Taxon:+String  generic_name
	Taxon:+String  subgenus
	Taxon:+String  specific_epithet
	Taxon:+String  infraspecific_epithet
	Taxon:+String  cultivar_epithet
	Taxon:+String  taxon_rank
	Taxon:+String  verbatim_taxon_rank
	Taxon:+String  scientific_name_authorship
	Taxon:+String  vernacular_name
	Taxon:+String  nomenclatural_code
	Taxon:+String  taxonomic_status
	Taxon:+Text  taxon_remarks
	Taxon:+String  parent_name_usage
	Taxon:+String  accepted_name_usage
	Taxon:+String  original_name_usage
	Taxon:+String  name_published_in
	Taxon:+String  name_according_to
	Taxon:+String  nomenclatural_status
	Taxon:+int  name_published_in_year
	Taxon:+Text  higher_classification
	Taxon:+String  nameAccordingToID
	Taxon:+String  scientific_name_id
	Taxon:+String  accepted_name_usage_id
	Taxon:+String  parent_name_usage_id
	Taxon:+String  name_published_in_id
	Taxon:+String  taxon_concept_id
	Taxon:+String  original_name_usage_id
	Taxon:+Text  sort_order
	Taxon:+Text  display_order
	Taxon:+  def __str__()
	Kingdom:+String name
	Kingdom:+DateTime update_date
	Kingdom:+ def __str__()
	TaxonomicUnits:+int tsn
	TaxonomicUnits:+PK kingdom_id
	TaxonomicUnits:+PK rank_id
	TaxonomicUnits:+String completename
	TaxonomicUnits:+String hierarchy_string
	TaxonomicUnits:+String hierarchy
	TaxonomicUnits:+String common_names
	TaxonomicUnits:+DateTime tsn_update_date
	TaxonomicUnits:+ def __str__()
	TaxonUnitTypes:+int rank_id
	TaxonUnitTypes:+String rank_name
	TaxonUnitTypes:+int dir_parent_rank_id
	TaxonUnitTypes:+int req_parent_rank_id
	TaxonUnitTypes:+DateTime update_date
	SynonymLinks:+FK tsn
	SynonymLinks:+FK tsn_accepted
	SynonymLinks:+String tsn_accepted_name
	SynonymLinks:+ def __str__()
	
	class Occurrence {
	+String occurrenceID
	+String eventID
	+String locationID
	+String taxonID
	
	+String catalogNumber
	+String recordNumber
	+String recordedBy
	+String recordedByID
	+int individualCount
	+String organismQuantity
	+String organismQuantityType
	+String sex
	+String lifeStage
	+String reproductiveCondition
	+String caste
	+String behavior
	+String vitality
	+String establishmentMeans
	+String degreeOfEstablishment
	+String pathway
	+String georeferenceVerificationStatus
	+String occurrenceStatus
	+String associatedMedia
	+String associatedOccurrences
	+String associatedReferences
	+String associatedTaxa
	+String otherCatalogNumbers
	+String occurrenceRemarks
	}
	
	class Event {
	+String eventID
	+String parentEventID
	
	+String eventType
	+String fieldNumber
	+String eventDate
	+String eventTime
	+int startDayOfYear
	+int endDayOfYear
	+int year
	+int month
	+int day
	+String verbatimEventDate
	+String habitat
	+String samplingProtocol
	+String sampleSizeValue
	+String sampleSizeUnit
	+String samplingEffort
	+String fieldNotes
	+String eventRemarks
	}
	
	class Location {
	+String locationID
	+String higherGeographyID
	+String higherGeography
	+String continent
	+String waterBody
	+String islandGroup
	+String island
	+String country
	+String countryCode
	+String stateProvince
	+String county
	+String municipality
	+String locality
	+String verbatimLocality
	+int minimumElevationInMeters
	+int maximumElevationInMeters
	+String verbatimElevation
	+String verticalDatum
	+int minimumDepthInMeters
	+int maximumDepthInMeters
	+String verbatimDepth
	+decimal minimumDistanceAboveSurfaceInMeters
	+decimal maximumDistanceAboveSurfaceInMeters
	+String locationAccordingTo
	+String locationRemarks
	+decimal decimalLatitude
	+decimal decimalLongitude
	+String geodeticDatum
	+int coordinateUncertaintyInMeters
	+decimal coordinatePrecision
	+decimal pointRadiusSpatialFit
	+String verbatimCoordinates
	+String verbatimLatitude
	+String verbatimLongitude
	+String verbatimCoordinateSystem
	+String verbatimSRS
	+String footprintWKT
	+String footprintSRS
	+decimal footprintSpatialFit
	+String georeferencedBy
	+String georeferencedDate
	+String georeferenceSources
	+String georeferenceRemarks
	}
	
	class Taxon {
	+String taxonID
	+String scientificNameID
	+String acceptedNameUsageID
	+String parentNameUsageID
	+String nameAccordingToID
	+String namePublishedInID̈́
	+String taxonConceptID
	+String scientificName
	+String acceptedNameUsage
	+String parentNameUsage
	+String originalNameUsage
	+String nameAccordingTo
	+String namePublishedIn
	+int namePublishedInYear
	+Text higherClassification
	+String kingdom
	+String phylum
	+String class
	+String order
	+String superfamily
	+String family
	+String subfamily
	+String tribe
	+String subtribe
	+String genus
	+String genericName
	+String subgenus
	+String infragenericEpithet
	+String specificEpithet
	+String infraspecificEpithet
	+String cultivarEpithet
	+String taxonRank
	+String verbatimTaxonRank
	+String scientificNameAuthorship
	+String vernacularName
	+String nomenclaturalCode
	+String taxonomicStatus
	+String nomenclaturalStatus
	+Text taxonRemarks
	}
```