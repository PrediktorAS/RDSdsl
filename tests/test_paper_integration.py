# Copyright 2021 Prediktor AS
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess
import time
from io import StringIO

import pandas as pd
import psycopg2
import pytest
from SPARQLWrapper import SPARQLWrapper

import quarry
import swt_translator as swtt
from .postgresql_time_series_database import SQLTimeSeriesDatabase
from rdstranslator import rdsquery_to_sparql
from rdsparser import parse_rdsquery

PATH_HERE = os.path.dirname(__file__)

@pytest.fixture(scope='module')
def create_ttl():
    namespaces = ['http://opcfoundation.org/UA/',
                  'http://prediktor.com/RDS_dsl_testcase',
                  'http://prediktor.com/RDS-Hydropower-Fragment',
                  'http://opcfoundation.org/UA/IEC61850-7-3',
                  'http://opcfoundation.org/UA/IEC61850-7-4',
                  'http://prediktor.com/IEC-61850-7-410-fragment'
                  ]

    output_file = PATH_HERE + '/expected/paper_integration/kb.ttl'

    swtt.translate(xml_dir=PATH_HERE + '/input_data/paper_integration', namespaces=namespaces,
                   output_ttl_file=output_file, subclass_closure=True, subproperty_closure=True,
                   signal_id_csv=PATH_HERE + '/input_data/paper_integration/signal_ids.csv')
    return output_file


@pytest.fixture(scope='module')
def set_up_endpoint(create_ttl):
    containername = 'fusekidocker'

    print("Cleaning up potential old containers...")
    try:
        subprocess.run('docker stop ' + containername, shell=True)
        subprocess.run('docker rm ' + containername, shell=True)
    except Exception as e:
        print("Nothing to clean or cleaning failed.")

    print("Cleaning done.")

    cmd = f'docker run -d -p 3030:3030 -v {PATH_HERE + "/expected/paper_integration"}:/usr/share/data --name {containername} atomgraph/fuseki --file=/usr/share/data/kb.ttl /ds'
    print(cmd)
    subprocess.run(cmd, shell=True)
    time.sleep(10)
    yield

    subprocess.run('docker stop ' + containername, shell=True)
    subprocess.run('docker rm ' + containername, shell=True)

@pytest.fixture(scope='module')
def sparql_endpoint(set_up_endpoint) -> SPARQLWrapper:
    return SPARQLWrapper('http://localhost:3030/ds/sparql')

@pytest.fixture(scope='module')
def pg_time_series_database(set_up_endpoint):
    params_dict = {
        "host": 'localhost',
        "database": 'postgres',
        "user": 'postgres',
        "port": '5445',
        "password": 'hemelipasor'
    }
    sqltsd = SQLTimeSeriesDatabase(params_dict=params_dict)
    return sqltsd

@pytest.fixture(scope='module')
def params():
    params_dict = {
        "host": 'localhost',
        "database": 'postgres',
        "user": 'postgres',
        "port": '5445',
        "password": 'hemelipasor'
    }
    return params_dict


@pytest.fixture(scope='module')
def postgresql(params):
    containername = 'postgresqlserver'
    volumename = 'postgresql'

    print("Cleaning up potential old containers...")
    try:
        subprocess.run('docker stop ' + containername, shell=True)
        subprocess.run('docker rm ' + containername, shell=True)
        subprocess.run('docker volume rm ' + volumename, shell=True)
    except Exception as e:
        print("Nothing to clean or cleaning failed.")

    print("Cleaning done.")

    cmd = f'docker run -d -v {volumename}:/var/lib/postgresql/data/ -e "POSTGRES_PASSWORD={params["password"]}" -p {params["port"]}:5432 --name {containername} postgres'
    subprocess.run(cmd, shell=True)
    time.sleep(10)
    yield

    subprocess.run('docker stop ' + containername, shell=True)
    subprocess.run('docker rm ' + containername, shell=True)
    subprocess.run('docker volume rm ' + volumename, shell=True)


@pytest.fixture(scope='module')
def timeseriesdata(postgresql, params):
    conn = psycopg2.connect(**params)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS TSDATA (ts TIMESTAMP, real_value REAL, bool_value BOOLEAN, signal_id INTEGER)')
    conn.commit()
    buffer = StringIO()
    df = pd.read_csv(PATH_HERE + '/input_data/paper_integration/signals.csv')
    df = df[['ts', 'real_value', 'bool_value', 'signal_id']]
    df.to_csv(buffer, index=False, header=False, sep='|', quotechar="'")
    buffer.seek(0)
    cursor = conn.cursor()
    cursor.copy_from(buffer, 'TSDATA', sep="|", null="")
    conn.commit()


def test_paper_query(sparql_endpoint, timeseriesdata, pg_time_series_database):
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
    actual_df = quarry.execute_query(sparql, sparql_endpoint, pg_time_series_database).reset_index(drop=True)
    #actual_df.to_csv(PATH_HERE + '/expected/paper_integration/basic2.csv', index=False)
    actual_df = actual_df[['designation', 'timestamp', 'HVLV_PosPct_mag', 'HVLV_Mvm_stVal']].copy()
    expected_df = pd.read_csv(PATH_HERE + '/expected/paper_integration/basic.csv')
    expected_df['timestamp'] = pd.to_datetime(expected_df['timestamp'])
    expected_df = expected_df[['designation', 'timestamp', 'HVLV_PosPct_mag', 'HVLV_Mvm_stVal']].copy()
    #ltx = actual_df.to_latex(index=False)
    #print(ltx)
    pd.testing.assert_frame_equal(actual_df, expected_df)