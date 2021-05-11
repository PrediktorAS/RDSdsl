from rdstranslator import rdsquery_to_sparql
from rdsparser import parse_rdsquery

def test_paperquery():
    q = """
=A=KA/HVLV.[1]
[1]PosPct.mag
[1]Mvm.stVal = true
from 2021-01-01 00:00:00+00:00
to 2021-01-31 23:59:59+00:00
"""
    rds_query = parse_rdsquery(qstr=q)
    sparql = rdsquery_to_sparql(query=rds_query)
    print(sparql)