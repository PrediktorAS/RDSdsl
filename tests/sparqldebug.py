from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

g = Graph()
g.parse("expected/paper_integration/kb.ttl", format="ttl")

q = prepareQuery(
    """SELECT ?designation ?timestamp ?HVLV_Mvm_stVal ?HVLV_PosPct_mag WHERE {
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
    FILTER(?timestamp > "2021-01-01T00:00:00+00:00Z"^^xsd:dateTime)
}""")

for row in qres:
    print(row)