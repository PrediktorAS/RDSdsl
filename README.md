# RDSdsl
A domain specific language for querying time series data for analytics from RDS (IEC 81346) 

Documentation is forthcoming (next week).
Included here is a parser for DSL queries over RDS / IEC 61850 information models like these:
```
=A=KA/HVLV.[1]
[1]PosPct.mag
[1]Mvm.stVal = true
from 2021-01-01 00:00:00+00:00
to 2021-01-31 23:59:59+00:00
```

We have a translator to SPARQL queries like the following (not tested yet):
```
SELECT ?designation ?timestamp ?HVLV.Mvm.stVal ?HVLV.PosPct.mag WHERE {
?HVLV <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <HVLV> .
?KA <http://opcfoundation.org/UA/IEC61850-7-3#hasLogicalNode> ?HVLV .
?HVLV <http://opcfoundation.org/UA/IEC61850-7-3#hasDataObject> ?PosPct .
?HVLV <http://opcfoundation.org/UA/IEC61850-7-3#hasDataObject> ?Mvm .
?PosPct <http://opcfoundation.org/UA/IEC61850-7-3#hasDataAttribute> ?mag .
?Mvm <http://opcfoundation.org/UA/IEC61850-7-3#hasDataAttribute> ?stVal .
?stVal <http://opcfoundation.org/UA/#value> ?stVal_Value .
?stVal_Value <http://opcfoundation.org/UA/#timestamp> ?timestamp .
?stVal_Value <http://opcfoundation.org/UA/#boolValue> ?HVLV.Mvm.stVal .
?mag <http://opcfoundation.org/UA/#value> ?mag_Value .
?mag_Value <http://opcfoundation.org/UA/#timestamp> ?timestamp .
?mag_Value <http://opcfoundation.org/UA/#realValue> ?HVLV.PosPct.mag .
SELECT DISTINCT ?designation ?KA WHERE {
?ROOT <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <ROOT> .
?A <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <A> .
?KA <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <KA> .
?KA <http://prediktor.com/RDS-Helpers/#hasCanonicalDesignation> ?designation .
?ROOT <http://prediktor.com/RDS-Helpers/#hasFunctionalAspect> ?A .
?A <http://prediktor.com/RDS-Helpers/#hasFunctionalAspect> ?KA .
}
}
```
