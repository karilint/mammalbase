SELECT 
 concat('https://www.mammalbase.net/ma/', master_attribute.`id`,'/') AS `traitID`
, master_entity.`name` AS `scientificName`
, master_attribute.`name` AS `traitName`
, round(source_measurement_value.`mean`*unit_conversion.coefficient,2) AS traitValue
, master_unit_2.print_name AS traitUnit
, source_entity.`name` AS `verbatimScientificName`
, source_attribute.`name` AS `verbatimTraitName`
, round(source_measurement_value.mean,2) AS verbatimTraitValue
, source_unit.name AS verbatimTraitUnit
, concat('https://www.mammalbase.net/me/', master_entity.`id`,'/') AS `taxonID`
, concat('https://www.mammalbase.net/smv/',source_measurement_value.id,'/') AS measurementID
, 'NA' occurrenceID
, case when entity_class.name not like '%species' then concat(entity_class.name, ' level data') else 'NA' end `warnings`
, entity_class.name AS `taxonRank`
, 'Animalia' AS kingdom
, 'Chordata' AS phylum
, 'Mammalia' AS class
, tdwg_taxon.`order` AS `order`
, tdwg_taxon.family AS family
, tdwg_taxon.genus AS genus
, 'literatureData' basisOfRecord
, master_reference.`type` AS `basisOfRecordDescription`
, replace(replace(master_reference.`citation`,'<i>',''),'</i>','') AS `references`
, case when entity_class.name not like '%species' then concat(entity_class.name, ' level data') else 'NA' end `measurementResolution`
, 'NA' measurementMethod
, 'NA' measurementDeterminedBy
, 'NA' measurementDeterminedDate
, 'NA' measurementRemarks
, case when source_measurement_value.n_total=1 then 'FALSE' else 'TRUE' end AS aggregateMeasure
, case when source_measurement_value.n_total=0 then 'NA' else source_measurement_value.n_total end AS individualCount
, case when source_measurement_value.std=0 then 'NA' else round(source_measurement_value.std*unit_conversion.coefficient,2) end AS dispersion
, case when (source_measurement_value.minimum*unit_conversion.coefficient)+(source_measurement_value.maximum*unit_conversion.coefficient) = 0 then 'NA' else round(source_measurement_value.minimum*unit_conversion.coefficient,2) end AS measurementValue_min
, case when (source_measurement_value.minimum*unit_conversion.coefficient)+(source_measurement_value.maximum*unit_conversion.coefficient) = 0 then 'NA' else round(source_measurement_value.maximum*unit_conversion.coefficient,2) end AS measurementValue_max
, source_measurement_value.measurement_accuracy AS measurementAccuracy
, source_statistic.name AS statisticalMethod
-- , case when smv.std=0 then 'NA' else case when round(smv.std,2) end AS statisticalMethod
, ifnull(orcid.uid, 'http://orcid.org/0000-0001-9627-8821') author
, NOW() issued
, (select MAX(date(modified_on)) FROM mb_dietsetitem) `version`

  from mb_masterentity master_entity
  join mb_entityrelation entity_relation
    on entity_relation.master_entity_id=master_entity.id
  join mb_sourceentity source_entity
    on source_entity.id=entity_relation.source_entity_id

  join `mb_entityclass` entity_class
    on((entity_class.`id` = master_entity.`entity_id`))

  join mb_sourcereference source_reference
    on source_reference.id=source_entity.reference_id
  join mb_masterreference master_reference
    on master_reference.id=source_reference.master_reference_id

  join mb_sourcemeasurementvalue source_measurement_value
    on source_measurement_value.source_entity_id=source_entity.id

  join mb_sourceattribute source_attribute
    on source_attribute.id=source_measurement_value.source_attribute_id
  join mb_attributerelation attribute_relation
    on attribute_relation.source_attribute_id=source_attribute.id
  join mb_masterattribute master_attribute
    on master_attribute.id=attribute_relation.master_attribute_id

  join mb_sourceunit source_unit
    on source_unit.id=source_measurement_value.source_unit_id

  join mb_unitrelation unit_relation
    on unit_relation.source_unit_id=source_measurement_value.source_unit_id
  join mb_masterunit master_unit_1
    on master_unit_1.id=unit_relation.master_unit_id
  join mb_masterunit master_unit_2
    on master_unit_2.id=master_attribute.unit_id

  left join mb_sourcestatistic source_statistic
    on source_statistic.id=source_measurement_value.source_statistic_id

  left join mb_unitconversion unit_conversion
    on unit_conversion.from_unit_id=master_unit_1.id
   and unit_conversion.to_unit_id=master_unit_2.id

  join `tdwg_taxon` tdwg_taxon
    on tdwg_taxon.TAXON_RANK=entity_class.name and tdwg_taxon.scientific_name=master_entity.name
JOIN auth_user a ON a.id=source_measurement_value.created_by_id
LEFT JOIN socialaccount_socialaccount orcid ON orcid.user_id=a.id



where master_attribute.`name` <> '- Checked, Unlinked -'
and (source_measurement_value.minimum*unit_conversion.coefficient)+(source_measurement_value.maximum*unit_conversion.coefficient) <> 0
 order by master_attribute.name