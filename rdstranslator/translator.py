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

from rdsparser import RDSQuery, QueryNode
from rdflib.term import Variable, URIRef, Literal
from rdflib.paths import MulPath
from rdflib import RDF
from .classes import Triple, Operator, Expression
from .query_generator import select_op_to_query

VALUE_VERB = 'http://opcfoundation.org/UA/#value'
STRING_VALUE_VERB = 'http://opcfoundation.org/UA/#stringValue'
REAL_VALUE_VERB = 'http://opcfoundation.org/UA/#realValue'
INT_VALUE_VERB = 'http://opcfoundation.org/UA/#intValue'
BOOL_VALUE_VERB = 'http://opcfoundation.org/UA/#boolValue'
TIMESTAMP_VERB = 'http://opcfoundation.org/UA/#timestamp'
BROWSENAME_VERB = 'http://opcfoundation.org/UA/#browseName'
HASCANONICALDESIGNATION_VERB = 'http://prediktor.com/RDS-Hydropower-Fragment#hasCanonicalDesignation'
RDS_HAS_LOGICAL_NODE_VERB = 'http://prediktor.com/RDS-Hydropower-Fragment#hasLogicalNode'
IEC61850_HAS_DATA_OBJECT_VERB = 'http://opcfoundation.org/UA/IEC61850-7-3#hasDataObject'
IEC61850_HAS_DATA_ATTRIBUTE_VERB = 'http://opcfoundation.org/UA/IEC61850-7-3#hasDataAttribute'
RDS_FUNCTIONAL_ASPECT_VERB = 'http://prediktor.com/RDS-Hydropower-Fragment#functionalAspect'
RDS_PRODUCT_ASPECT_VERB = 'http://prediktor.com/RDS-Hydropower-Fragment#productAspect'
RDS_CONSTRUCTION_ASPECT_VERB = 'http://prediktor.com/RDS-Hydropower-Fragment#constructionAspect'
RDS_TYPE_ASPECT_VERB = 'http://prediktor.com/RDS-Hydropower-Fragment#hasTypeAspect'
RDS_TYPE_PREFIX = 'http://prediktor.com/RDS-Hydropower-Fragment#'
IEC61850_TYPE_PREFIX = 'http://prediktor.com/IEC-61850-7-410-fragment#'

attrib_datatype_dict = {
    'stVal':BOOL_VALUE_VERB,
    'mag':REAL_VALUE_VERB
}

def rdsquery_to_sparql(query:RDSQuery):

    slash_edges = [e for e in query.gr.edges(data='edge_type') if e[2] == '/']
    distinct_rds_nodes = {e[0] for e in slash_edges}
    logical_nodes = {e[1] for e in slash_edges}

    for n in distinct_rds_nodes:
        pass
        #TODO: add designation col, bind to canonical designation

    data_objects = {e[1] for e in query.gr.out_edges(logical_nodes)}
    data_attributes = {e[1] for e in query.gr.out_edges(data_objects)}
    #TODO check nothing lower than data attributes

    da_path_dict = {}
    for ln in logical_nodes:
        for do in query.gr.out_edges(ln):
            for da in query.gr.out_edges(do[1]):
                da_path = ln.identifier + '_' + do[1].identifier + '_' + da[1].identifier
                da_path_dict[da[1]] = da_path

    var_dict = {}

    used_names = set()
    for n in query.gr.nodes:
        name = n.identifier
        while name in used_names:
            name = name + '_1'
        var_dict[n] = Variable(name)

    #Begin creating query, we use the algebraic structure of RDFLib
    matselop = Operator(type='SelectQuery', name='MatrixSelectQuery')
    matprojop = Operator(type='Project', name='MatrixProject')
    matfilterop = Operator(type='Filter', name='MatrixFilter')
    matjoinop = Operator(type='Join', name='MatrixJoin')
    matbgpop = Operator(type='BGP', name='MatrixBGP')

    matselop.children.append(matprojop)
    matprojop.children.append(matfilterop)
    matfilterop.children.append(matjoinop)
    matjoinop.children.append(matbgpop)

    subtomultisetop = Operator(type='ToMultiSet', name='SubToMultiset')
    subdistinctop = Operator(type='Distinct', name='SubDistinct')
    subprojop = Operator(type='Project', name='SubProject')
    subbgpop = Operator(type='BGP', name='SubBGP')

    matjoinop.children.append(subtomultisetop)
    subtomultisetop.children.append(subdistinctop)
    subdistinctop.children.append(subprojop)
    subprojop.children.append(subbgpop)

    for n in query.gr.nodes:
        if n in logical_nodes.union(data_objects).union(data_attributes):
            useop = matbgpop
        else:
            useop = subbgpop

        if n not in data_attributes.union(data_objects):
            if n.identifier.isalpha():
                if n in logical_nodes:
                    typeuri = IEC61850_TYPE_PREFIX + n.identifier
                else:
                    typeuri = RDS_TYPE_PREFIX + n.identifier
                useop.triples.append(Triple(subject=var_dict[n], verb=RDF.type, object=URIRef(typeuri)))
            else:
                useop.triples.append(Triple(subject=var_dict[n], verb=URIRef(BROWSENAME_VERB), object=Literal(n.identifier)))
        else:
            useop.triples.append(
                Triple(subject=var_dict[n], verb=URIRef(BROWSENAME_VERB), object=Literal(n.identifier)))

    i=0
    for n in distinct_rds_nodes:
        if i == 0:
            name = 'designation'
        else:
            name = 'designation_' + str(i)

        designation_var = Variable(name)
        #Find canonical designation of RDS-node before slash, here we have encoded it on the browsename for simplicity.
        subbgpop.triples.append(Triple(subject=var_dict[n], verb=URIRef(BROWSENAME_VERB), object=designation_var))

        #Project canonical designation of RDS-node before slash from subquery
        subprojop.project_vars.append(designation_var)

        #Project URI of RDS-node before slash from subquery
        subprojop.project_vars.append(var_dict[n])

        #Project canonical designation of RDS-node before slash from matrix query
        matprojop.project_vars.append(designation_var)

    for e in query.gr.edges(data=True):
        if e[1] in logical_nodes.union(data_objects).union(data_attributes):
            useop = matbgpop
        else:
            useop = subbgpop

        if e[2]['edge_type'] == '.':
            if e[1] in data_objects:
                edge_type = IEC61850_HAS_DATA_OBJECT_VERB
            elif e[1] in data_attributes:
                edge_type = IEC61850_HAS_DATA_ATTRIBUTE_VERB
            else:
                raise SyntaxError('. where it does not belong')
        elif e[2]['edge_type'] == '=':
            edge_type = RDS_FUNCTIONAL_ASPECT_VERB
        elif e[2]['edge_type'] == '+':
            edge_type = RDS_CONSTRUCTION_ASPECT_VERB
        elif e[2]['edge_type'] == '#':
            edge_type = RDS_TYPE_ASPECT_VERB
        elif e[2]['edge_type'] == '/':
            edge_type = RDS_HAS_LOGICAL_NODE_VERB
        else:
            raise SyntaxError('Unknown edge type: ' + e[2]['edge_type'])

        if e[2]['ellipsis']:
            verb = MulPath(path=edge_type, mod='+')
        else:
            verb = URIRef(edge_type)

        #Add appropriate structural constraints encoding aspects, slash and navigation to data attributes with dot.
        useop.triples.append(Triple(subject=var_dict[e[0]], verb=verb, object=var_dict[e[1]]))

    da_value_var_dict = {}

    for da in data_attributes:
        da_value_var_dict[da] = Variable(da_path_dict[da])

    timestamp_var = Variable('timestamp')
    #Project the timestamp from the matrix query
    matprojop.project_vars.append(timestamp_var)

    for da in data_attributes:
        da_var = var_dict[da]
        da_value_holder = Variable(str(da_var) + '_Value')
        #Extract the value, timestamp of all data attributes
        matbgpop.triples.append(Triple(subject=da_var, verb=URIRef(VALUE_VERB), object=da_value_holder))
        matbgpop.triples.append(Triple(subject=da_value_holder, verb=URIRef(TIMESTAMP_VERB), object=timestamp_var))
        da_value_var = da_value_var_dict[da]
        datatype_verb = attrib_datatype_dict[da.identifier]
        matbgpop.triples.append(Triple(subject=da_value_holder, verb=URIRef(datatype_verb), object=da_value_var))
        #Project data attribute values from matrix query
        matprojop.project_vars.append(da_value_var)

    if query.from_dt is not None:
        from_expr = Expression(lhs=timestamp_var, op='>=', rhs=Literal(query.from_dt))
        matfilterop.expressions.append(from_expr)
    if query.to_dt is not None:
        to_expr = Expression(lhs=timestamp_var, op='<=', rhs=Literal(query.to_dt))
        matfilterop.expressions.append(to_expr)

    for f in query.query_filters:
        if type(f.rhs) == QueryNode:
            rhs = da_value_var_dict[f.rhs]
        else:
            rhs = Literal(f.rhs)
        f_expr = Expression(lhs=da_value_var_dict[f.lhs], op=f.op, rhs=rhs)
        matfilterop.expressions.append(f_expr)

    q = select_op_to_query(matselop)
    return q
