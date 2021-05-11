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
