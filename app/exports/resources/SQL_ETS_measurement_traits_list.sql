SELECT 
 concat('https://www.mammalbase.net/ma/', `ma`.`id`,'/') AS `traitID`
, `me`.`name` AS `scientificName`
, `ma`.`name` AS `traitName`
, round(`smv`.`mean`*uc.coefficient,2) AS traitValue
, mu.print_name AS traitUnit
, `se`.`name` AS `verbatimScientificName`
, `sa`.`name` AS `verbatimTraitName`
, round(smv.mean,2) AS verbatimTraitValue
, su.name AS verbatimTraitUnit
, concat('msw3:', msw3.taxon_id) AS `taxonID`
-- , concat('https://www.mammalbase.net/me/', `me`.`id`,'/') AS `taxonID`
, concat('https://www.mammalbase.net/smv/',smv.id,'/') AS measurementID
, 'NA' occurrenceID
, case when ec.name not like '%species' then concat(ec.name, ' level data') else 'NA' end `warnings`
, ec.name AS `taxonRank`
, 'Animalia' AS kingdom
, 'Chordata' AS phylum
, 'Mammalia' AS class
, msw3.`order` AS `order`
, msw3.family AS family
, msw3.genus AS genus
, 'literatureData' basisOfRecord
, mr.`type` AS `basisOfRecordDescription`
, replace(replace(mr.`citation`,'<i>',''),'</i>','') AS `references`
, case when ec.name not like '%species' then concat(ec.name, ' level data') else 'NA' end `measurementResolution`
, 'NA' measurementMethod
, smv.measured_by AS measurementDeterminedBy
, 'NA' measurementDeterminedDate
, smv.remarks AS measurementRemarks
, case when smv.n_total=1 then 'FALSE' else 'TRUE' end AS aggregateMeasure
, case when smv.n_total=0 then 'NA' else smv.n_total end AS individualCount
, case when smv.std=0 then 'NA' else round(smv.std*uc.coefficient,2) end AS dispersion
, case when (smv.minimum*uc.coefficient)+(smv.maximum*uc.coefficient) = 0 then 'NA' else round(smv.minimum*uc.coefficient,2) end AS measurementValue_min
, case when (smv.minimum*uc.coefficient)+(smv.maximum*uc.coefficient) = 0 then 'NA' else round(smv.maximum*uc.coefficient,2) end AS measurementValue_max
, smv.measurement_accuracy AS measurementAccuracy
, st.name AS statisticalMethod
, gender.caption AS sex
, lifestage.caption AS lifeStage
, 'NA' AS age
, 'NA' AS morphotype
, 'NA' AS eventID
, 'NA' AS preparations
, 'NA' AS samplingProtocol
, 'NA' AS `year`
, 'NA' AS `month`
, 'NA' AS `day`
, 'NA' AS `eventDate`
, 'NA' AS `locationID`
, 'NA' AS habitat
, 'NA' AS decimalLongitude
, 'NA' AS decimalLatitude
, 'NA' AS elevation
, 'NA' AS geodeticDatum
, sl.name AS verbatimLocality
, 'NA' AS country
, 'NA' AS countryCode
, 'NA' AS occurrenceRemarks


, 'http://urn.fi/urn:nbn:fi:att:8dce459f-1401-4c6a-b2bb-c831bd8d3d6f' datasetID
, 'MammalBase — Dataset 03: Trait Data in Ecological Trait-data Standard (ETS) format' datasetName
, 'MammalBase - www.mammalbase.net: Trait dataset output in Ecological Trait-data Standard (ETS)' datasetDescription
, ifnull(orcid.uid, 'http://orcid.org/0000-0001-9627-8821') author
, NOW() issued
, DATE_FORMAT(now(), '%Y-%m-%dT%H:%i+02:00') `version`
, concat('The MammalBase community ',YEAR(NOW()),' , Data version ', DATE_FORMAT(now(), "%D %M %Y"),' at https://mammalbase.org/me/') bibliographicCitation
, 'Ecological Trait-data Standard Vocabulary; v0.10; URL: https://terminologies.gfbio.org/terms/ets/pages/; URL: https://doi.org/10.5281/zenodo.1485739' conformsTo
, 'Lintulaakso, Kari;https://orcid.org/0000-0001-9627-8821;Finnish Museum of Natural History LUOMUS' rightsHolder
, 'Attribution 4.0 International (CC BY 4.0)' rights
, 'CC BY 4.0' license


, concat('https://www.mammalbase.net/ma/', `ma`.`id`,'/') AS `identifier`
, REPLACE(`ma`.`name`, " ", "_") AS `trait`
, mag.name AS `broaderTerm`
, 'NA' AS narrowerTerm
, 'NA' AS relatedTerm
, mu.quantity_type AS valueType
, mu.print_name AS `expectedUnit`
, 'NA' AS factorLevels
, 'NA' AS maxAllowedValue
, 'NA' AS minAllowedValue
, ma.remarks AS traitDescription
, 'NA' AS comments
, mar.citation AS `source`

  from mb_masterentity me
  join mb_entityrelation er
    on er.master_entity_id=me.id
  join mb_sourceentity se
    on se.id=er.source_entity_id
  join `mb_entityclass` `ec`
    on((`ec`.`id` = `me`.`entity_id`)) 
  join mb_sourcereference sr
    on sr.id=se.reference_id
  join mb_masterreference mr
    on mr.id=sr.master_reference_id
  join mb_sourcemeasurementvalue smv
    on smv.source_entity_id=se.id
  join mb_sourceattribute sa
    on sa.id=smv.source_attribute_id
  join mb_attributerelation ar
    on ar.source_attribute_id=sa.id
  join mb_masterattribute ma
    on ma.id=ar.master_attribute_id
  join mb_sourceunit su
    on su.id=smv.source_unit_id
  join mb_unitrelation ur
    on ur.source_unit_id=smv.source_unit_id
  join mb_masterunit u
    on u.id=ur.master_unit_id
  join mb_masterunit mu
    on mu.id=ma.unit_id
  JOIN mb_masterreference mar
    ON mar.id=ma.reference_id
  left join mb_sourcestatistic st
    on st.id=smv.source_statistic_id
  left join mb_sourcelocation sl
    on sl.id=smv.source_location_id
  left join mb_unitconversion uc
    on uc.from_unit_id=u.id
   and uc.to_unit_id=mu.id
  LEFT JOIN mb_choicevalue gender
    ON gender.id=smv.gender_id AND gender.choice_set='Gender'
  LEFT JOIN mb_choicevalue lifestage
    ON lifestage.id=smv.life_stage_id AND lifestage.choice_set='Lifestage'
  LEFT JOIN mb_attributegrouprelation agr
    ON agr.attribute_id=ma.id
  LEFT JOIN mb_masterattributegroup mag
    ON mag.id=agr.group_id
  join `tdwg_taxon` msw3
    on msw3.TAXON_RANK=ec.name and msw3.scientific_name=me.name
JOIN auth_user a ON a.id=smv.created_by_id
LEFT JOIN socialaccount_socialaccount orcid ON orcid.user_id=a.id



where `ma`.`name` <> '- Checked, Unlinked -'
and (smv.minimum*uc.coefficient)+(smv.maximum*uc.coefficient) <> 0
 order by ma.name