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

import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="RDSdsl",
    version="0.0.1",
    description="A domain specific language for querying time series data for analytics from RDS (IEC 81346)",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/PrediktorAS/RDSdsl",
    author="Magnus Bakken",
    author_email="mba@prediktor.com",
    license="Apache License 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["rdsparser", "rdstranslator"],
    include_package_data=True,
    install_requires=[
        "antlr4-python3-runtime>=4.9.2",
        "antlr4-python3-runtime<5.0",
        "networkx>=2.5.1",
        "python-dateutil",
        "rdflib>=5.0.0",
        "rdflib<6.0"
    ])