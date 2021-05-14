from rdflib import Graph

g = Graph()
g.parse("expected/paper_integration/kb.ttl", format="ttl")

qres = g.query(
    """SELECT ?designation ?stVal ?mag WHERE {
?Mvm <http://opcfoundation.org/UA/IEC61850-7-3#hasDataAttribute> ?stVal.
?mag_Value <http://prediktor.com/UA-helpers/#signalId> ?mag_Value_signal_id.
?HVLV <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://prediktor.com/IEC-61850-7-410-fragment#HVLV>.
?HVLV <http://opcfoundation.org/UA/IEC61850-7-3#hasDataObject> ?Mvm.
?PosPct <http://opcfoundation.org/UA/IEC61850-7-3#hasDataAttribute> ?mag.
?HVLV <http://opcfoundation.org/UA/IEC61850-7-3#hasDataObject> ?PosPct.
?mag <http://opcfoundation.org/UA/#value> ?mag_Value.
?stVal <http://opcfoundation.org/UA/#value> ?stVal_Value.
?stVal_Value <http://prediktor.com/UA-helpers/#signalId> ?stVal_Value_signal_id.
?KA <http://prediktor.com/RDS-Hydropower-Fragment#hasLogicalNode> ?HVLV.
?SiteType <http://prediktor.com/RDS-Hydropower-Fragment#functionalAspect> ?A.
?A <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://prediktor.com/RDS-Hydropower-Fragment#A>.
?SiteType <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://prediktor.com/RDS-Hydropower-Fragment#SiteType>.
?A <http://prediktor.com/RDS-Hydropower-Fragment#functionalAspect> ?KA.
?KA <http://opcfoundation.org/UA/#browseName> ?designation.
?KA <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://prediktor.com/RDS-Hydropower-Fragment#KA>.
}""")

for row in qres:
    print(row)