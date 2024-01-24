```mermaid
classDiagram
    class Occurrence {
		+String occurrenceID
		+String eventID
		+String locationID
		+String taxonID
		+String organismQuantity
		+String organismQuantityType
		+String sex
		+String lifeStage
		+String verbatimEventDate
		+String occurrenceRemarks
		+FK associatedReferences
    }
    class Event {
		+String eventID
		+String parentEventID
		+String samplingProtocol
		+String habitatType
		+int habitatPercentage
    }
    class Location {
      	+String verbatimLocality
		+String verbatimElevation
		+String verbatimDepth
		+float verbatimLatitude
		+float verbatimLongitude
		+String verbatimCoordinateSystem
		+String verbatimSRS
    }
    class Taxon {
      	+String taxonID
    }

    Occurrence "1" -- "0.." Event : eventID
    Occurrence "1" -- "0.." Location : locationID
    Occurrence "0.." -- "0.." Taxon : taxonID
```