# RDSdsl
A domain specific language for querying time series data for analytics from RDS (IEC 81346) composed with IEC-61850.

Included here is:
- A prototype parser
- A prototype translator to SPARQL
- A test case demonstrating how we can combine this package with [Quarry](https://github.com/PrediktorAS/quarry) to query time series data which are contextualized by RDS and IEC 61850.

Included here is a parser for DSL queries over RDS / IEC 61850 information models like these:

## Overview

### Queries
Queries are based on RDS (IEC 81346) notation and IEC 61850 syntax for data attributes.
All queries are implicitly about identifying a set of signals and extracting the time series for these signals in an interval meeting conditions specified by the user. 
```
=A=KA/HVLV.[1]
[1]PosPct.mag
[1]Mvm.stVal = true
from 2021-01-01 00:00:00+00:00
to 2021-01-31 23:59:59+00:00
```
The grammar in Antlr4 notation can be found [here](https://github.com/PrediktorAS/RDSdsl/blob/main/parsergenerator/rdsquery.g4).
The parser converts queries such as these to the abstract syntax defined in the paper. 

### Translation to SPARQL
The included translation script operates on abstract syntax objects and creates corresponding SPARQL queries like these:
```
SELECT ?designation ?timestamp ?HVLV_Mvm_stVal ?HVLV_PosPct_mag WHERE {
    ?HVLV <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://prediktor.com/IEC-61850-7-410-fragment#HVLV> .
    ?PosPct <http://opcfoundation.org/UA/#browseName> "PosPct" .
    ?mag <http://opcfoundation.org/UA/#browseName> "mag" .
    ?Mvm <http://opcfoundation.org/UA/#browseName> "Mvm" .
    ?stVal <http://opcfoundation.org/UA/#browseName> "stVal" .
    ?KA <http://prediktor.com/RDS-Hydropower-Fragment#hasLogicalNode> ?HVLV .
    ?HVLV <http://opcfoundation.org/UA/IEC61850-7-3#hasDataObject> ?PosPct .
    ?HVLV <http://opcfoundation.org/UA/IEC61850-7-3#hasDataObject> ?Mvm .
    ?PosPct <http://opcfoundation.org/UA/IEC61850-7-3#hasDataAttribute> ?mag .
    ?Mvm <http://opcfoundation.org/UA/IEC61850-7-3#hasDataAttribute> ?stVal .
    ?stVal <http://opcfoundation.org/UA/#value> ?stVal_Value .
    ?stVal_Value <http://opcfoundation.org/UA/#timestamp> ?timestamp .
    ?stVal_Value <http://opcfoundation.org/UA/#boolValue> ?HVLV_Mvm_stVal .
    ?mag <http://opcfoundation.org/UA/#value> ?mag_Value .
    ?mag_Value <http://opcfoundation.org/UA/#timestamp> ?timestamp .
    ?mag_Value <http://opcfoundation.org/UA/#realValue> ?HVLV_PosPct_mag .
    {
    SELECT DISTINCT ?designation ?KA WHERE {
        ?SiteType <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://prediktor.com/RDS-Hydropower-Fragment#SiteType> .
        ?A <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://prediktor.com/RDS-Hydropower-Fragment#A> .
        ?KA <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://prediktor.com/RDS-Hydropower-Fragment#KA> .
        ?KA <http://opcfoundation.org/UA/#browseName> ?designation .
        ?SiteType <http://prediktor.com/RDS-Hydropower-Fragment#functionalAspect> ?A .
        ?A <http://prediktor.com/RDS-Hydropower-Fragment#functionalAspect> ?KA .
        }
    }
    FILTER( ?timestamp >= "2021-01-01T00:00:00+00:00"^^<http://www.w3.org/2001/XMLSchema#dateTime> 
            && ?timestamp <= "2021-01-31T23:59:59+00:00"^^<http://www.w3.org/2001/XMLSchema#dateTime>
            && ?HVLV_Mvm_stVal = "true"^^<http://www.w3.org/2001/XMLSchema#boolean>)

}
```
### Results

Using a setup such as in [Quarry](https://github.com/PrediktorAS/quarry), we can query a SPARQL database together with a time series database and get the following result:

|designation|timestamp|HVLV_Mvm_stVal|HVLV_PosPct_mag|
|-----------|---------|--------------|---------------|
|<MySite>=A1.KA1|2021-01-01 00:00:00|True|10.0|
|<MySite>=A1.KA1|2021-01-03 00:00:00|True|12.0|
|<MySite>=A1.KA1|2021-01-04 00:00:00|True|13.0|
|<MySite>=A1.KA1|2021-01-05 00:00:00|True|14.0|
|<MySite>=A1.KA1|2021-01-31 10:00:00|True|15.0|
|<MySite>=A2.KA1|2021-01-01 00:00:00|True|20.0|
|<MySite>=A2.KA1|2021-01-02 00:00:00|True|21.0|
|<MySite>=A2.KA1|2021-01-03 00:00:00|True|22.0|
|<MySite>=A2.KA1|2021-01-04 00:00:00|True|23.0|
|<MySite>=A2.KA1|2021-01-05 00:00:00|True|24.0|
|<MySite>=A2.KA1|2021-01-31 10:00:00|True|25.0|
