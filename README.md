<img src="images/logo.png" alt="Logo by Adrian Rutle"/>

A domain specific language for querying time series data for analytics from RDS (IEC 81346) composed with IEC-61850.

Included here is:
- A prototype parser in Python
- A prototype translator to SPARQL using Python
- A [test case](https://github.com/PrediktorAS/RDSdsl/blob/main/tests/test_paper_integration.py) demonstrating how we can combine this package with [Quarry](https://github.com/PrediktorAS/quarry) to query time series data which are contextualized by RDS and IEC 61850.

This repository is associated with a paper, a draft version of which can be viewed [here](paperlink).

## Usage
### Installing
Use the following command to install:
```
pip install git+https://github.com/PrediktorAS/RDSdsl.git
```
### Running tests
Assuming Python 3 is installed, and you are in the folder where the repo has been cloned, run:
```
pip install .
pip install -r tests/requirements.txt
pytest
```

### Example usage
There are two functions of interest, the ```parse_rdsquery```-functions parses a query string and gives us a graph-based representation of the query.
The ```rdsquery_to_sparql```-function translates a parsed query to a SPARQL-string.
```python
from rdstranslator import rdsquery_to_sparql
from rdsparser import parse_rdsquery 

q = """=A=KA/HVLV.[1]
[1]PosPct.mag
[1]Mvm.stVal = true
from 2021-01-01 00:00:00+00:00
to 2021-01-31 23:59:59+00:00
"""
rds_query = parse_rdsquery(qstr=q)
sparql = rdsquery_to_sparql(query=rds_query)
```
## Overview
### Models
We wish to query the time series data sets associated with industrial assets that are contextualized using the IEC 81346 (RDS) and IEC-61850 standards, and assume that you are somewhat familiar with these standards if you have found your way here.
With our queries we would like to specify collections of logical devices using the RDS, and specify signals of interest attached to these devices using logical node types, data object names and data attribute names.
From the paper above, we have the following example model:

<img src="images/paper_model.png" alt="Model from paper" width="350px"/>

Now, there is time series data attached to the leaf nodes in this tree, and we would like to access it with our query. 
### Queries
Queries are based on RDS (IEC 81346) notation and IEC 61850 syntax for data attributes.
All queries are implicitly about identifying a set of signals and extracting the time series for these signals in an interval meeting conditions specified by the user. 
The query below extracts time series data associated with the leaf nodes in our example, but only for a certain period and only when Mvm.stVal is true. 
```
=A=KA/HVLV.[1]
[1]PosPct.mag
[1]Mvm.stVal = true
from 2021-01-01 00:00:00+00:00
to 2021-01-31 23:59:59+00:00
```

In the example above, we want the signals called PosPct.mag and Mvm.stVal attached to a logical node of type HVLV where this node is attached to a logical device which is:
- reached from the root by navigating using the functional aspect (=) to a node with class code A
- from there navigating with the functional aspect (=) to a node with class code KA

PosPct is the name of a data object, mag a data attribute. 
The IEC 61850-7-410 specification states that HVLV nodes can have data objects called PosPct and that these again have mag data attributes. 
See the associated [paper](paperlink) for a more detailed discussion of syntax and intended semantics.

The grammar in Antlr4 notation can be found [here](https://github.com/PrediktorAS/RDSdsl/blob/main/parsergenerator/rdsquery.g4).

### Translation to SPARQL
The included translation script operates on abstract syntax objects and creates corresponding SPARQL queries like these:

<details>
    <summary>Show code</summary>

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
</details>

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

## License
The code in this repository is copyrighted to [Prediktor AS](http://prediktor.com), and is licensed under the Apache 2.0 license. \
Exceptions apply to some of the test data (see document headers for license information). 

Author:
[Magnus Bakken](https://magbak.github.io)

Logo design by Professor Adrian Rutle at the Western Norway University of Applied Sciences.
