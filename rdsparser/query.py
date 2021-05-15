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
import networkx as nx
from typing import Optional, Dict, Tuple, Union, List
import uuid
from datetime import datetime

@dataclass
class QueryNode:
    identifier: str

    uid: str = field(default_factory=lambda:str(uuid.uuid4()))

    def __hash__(self):
        return self.uid.__hash__()


@dataclass
class QueryFilter:
    lhs: QueryNode
    rhs: Union[QueryNode, int, float, bool]
    op: str


@dataclass
class RDSQuery:
    root: QueryNode
    glue_dict: Dict[int, Tuple[QueryNode, str, bool]] = field(default_factory=dict)
    gr: nx.MultiDiGraph = field(default_factory=nx.MultiDiGraph)
    query_filters: List[QueryFilter] = field(default_factory=list)
    from_dt: datetime = field(default=None)
    to_dt: datetime = field(default=None)
