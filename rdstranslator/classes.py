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

from dataclasses import dataclass, field
from typing import List, Set, Union

from rdflib.term import Variable, URIRef, Literal


@dataclass
class Triple:
    subject: Union[Variable, URIRef, Literal]
    verb: URIRef
    object: Union[Variable, URIRef, Literal]


@dataclass
class Expression:
    lhs: Variable
    op: str
    rhs: Union[Variable, Literal]

@dataclass
class Operator:
    type: str
    name: str
    triples: List[Triple] = field(default_factory=list)
    children: List['Operator'] = field(default_factory=list)
    project_vars: List[Variable] = field(default_factory=list)
    distinct: bool = field(default=False)
    expressions: List[Expression] = field(default_factory=list)
