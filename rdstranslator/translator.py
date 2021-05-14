from rdsparser import RDSQuery
from rdflib.term import Variable, URIRef, Literal
from rdflib.paths import MulPath
from rdflib import RDF
from .classes import Triple, Operator
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

    #Begin creating query

    matop = Operator(type='SelectQuery', name='MatrixQuery')
    matbgpop = Operator(type='BGP', name='SignalsQuery')
    rdsselop = Operator(type='SelectQuery', name='RDSSubSelect', distinct=True)
    rdsbpgop = Operator(type='BGP', name='RDSBGP', distinct=True)

    matop.children.append(matbgpop)
    matop.children.append(rdsselop)
    rdsselop.children.append(rdsbpgop)

    for n in query.gr.nodes:
        if n in logical_nodes.union(data_objects).union(data_attributes):
            useop = matbgpop
        else:
            useop = rdsbpgop

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
        rdsbpgop.triples.append(Triple(subject=var_dict[n], verb=URIRef(BROWSENAME_VERB), object=designation_var))
        rdsselop.project_vars.append(designation_var)
        rdsselop.project_vars.append(var_dict[n])
        matop.project_vars.append(designation_var)

    for e in query.gr.edges(data=True):
        if e[1] in logical_nodes.union(data_objects).union(data_attributes):
            useop = matbgpop
        else:
            useop = rdsbpgop

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

        useop.triples.append(Triple(subject=var_dict[e[0]], verb=verb, object=var_dict[e[1]]))

    da_value_var_dict = {}

    for da in data_attributes:
        da_value_var_dict[da] = Variable(da_path_dict[da])

    timestamp_var = Variable('timestamp')
    matop.project_vars.append(timestamp_var)

    for da in data_attributes:
        da_var = var_dict[da]
        da_value_holder = Variable(str(da_var) + '_Value')
        matbgpop.triples.append(Triple(subject=da_var, verb=URIRef(VALUE_VERB), object=da_value_holder))
        matbgpop.triples.append(Triple(subject=da_value_holder, verb=URIRef(TIMESTAMP_VERB), object=timestamp_var))
        da_value_var = da_value_var_dict[da]
        datatype_verb = attrib_datatype_dict[da.identifier]
        matbgpop.triples.append(Triple(subject=da_value_holder, verb=URIRef(datatype_verb), object=da_value_var))
        matop.project_vars.append(da_value_var)

    q = select_op_to_query(matop, False)
    return q
