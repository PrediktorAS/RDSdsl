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
A translator creates corresponding SPARQL queries like these:
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
}
```
Yielding results such as:
```
designation,timestamp,HVLV_Mvm_stVal,HVLV_PosPct_mag
<MySite>=A1.KA1,2021-01-01 00:00:00,True,10.0
<MySite>=A1.KA1,2021-01-02 00:00:00,False,11.0
<MySite>=A1.KA1,2021-01-03 00:00:00,True,12.0
<MySite>=A1.KA1,2021-01-04 00:00:00,True,13.0
<MySite>=A1.KA1,2021-01-05 00:00:00,True,14.0
<MySite>=A1.KA1,2021-01-31 10:00:00,True,15.0
<MySite>=A1.KA1,2021-02-01 00:00:00,True,16.0
<MySite>=A2.KA1,2021-01-01 00:00:00,True,20.0
<MySite>=A2.KA1,2021-01-02 00:00:00,True,21.0
<MySite>=A2.KA1,2021-01-03 00:00:00,True,22.0
<MySite>=A2.KA1,2021-01-04 00:00:00,True,23.0
<MySite>=A2.KA1,2021-01-05 00:00:00,True,24.0
<MySite>=A2.KA1,2021-01-31 10:00:00,True,25.0
<MySite>=A2.KA1,2021-02-01 00:00:00,True,26.0
```