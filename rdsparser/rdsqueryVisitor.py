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

from antlr4 import *
from .rdsqueryParser import rdsqueryParser
from .query import RDSQuery, QueryNode, QueryFilter
from dateutil import parser

def cdict(ctx):
    d = {}
    for c in ctx.getChildren():
        thetype = type(c).__name__.replace('Context', '')
        if thetype in d:
            d[thetype].append(c)
        else:
            d[thetype] = [c]
    return d

def extract_glue(glue:str) -> int:
    return int(glue.replace('[', '').replace(']', ''))


class rdsqueryVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by rdsqueryParser#rdsQuery.
    def visitRdsQuery(self, ctx:rdsqueryParser.RdsQueryContext):
        cd = cdict(ctx)

        rds_query = RDSQuery(root=QueryNode('SiteType'))
        qec = 'QueryExpression'
        if qec in cd:
            for q in cd[qec]:
                self.visitQueryExpression(q, rds_query)

        if ctx.fromdt is not None:
            rds_query.from_dt = self.visitDateTime(ctx.fromdt)
        if ctx.todt is not None:
            rds_query.to_dt = self.visitDateTime(ctx.todt)

        return rds_query

    # Visit a parse tree produced by rdsqueryParser#queryExpression.
    def visitQueryExpression(self, ctx:rdsqueryParser.QueryExpressionContext, rds_query:RDSQuery):
        cd = cdict(ctx)
        dexpr = 'DesignationExpr'
        if dexpr in cd:
            for c in cd[dexpr]:
                self.visitDesignationExpr(c, rds_query)

        gse = 'GluedSignalExpr'
        if gse in cd:
            for c in cd[gse]:
                self.visitGluedSignalExpr(c, rds_query)


    # Visit a parse tree produced by rdsqueryParser#designationExpr.
    def visitDesignationExpr(self, ctx:rdsqueryParser.DesignationExprContext, rds_query:RDSQuery):
        cd = cdict(ctx)
        last_designation = None
        for sd in cd['SingleDesignation']:
            last_designation = self.visitSingleDesignation(sd, rds_query, last_designation)

        if ctx.signal_expr is not None:
            self.visitSignalExpr(ctx.signal_expr, rds_query, last_designation, '/')

    # Visit a parse tree produced by rdsqueryParser#singleDesignation.
    def visitSingleDesignation(self, ctx:rdsqueryParser.SingleDesignationContext,
                               rds_query:RDSQuery, last_designation:QueryNode):
        prefix = ''.join(c.symbol.text for c in ctx.prefix.children)

        identifier = ctx.identifier.text
        if ctx.glue is not None:
            glue = extract_glue(ctx.glue.text)
        else:
            glue = None

        if ctx.ellipsis is not None:
            ellipsis = True
        else:
            ellipsis = False

        designation = QueryNode(identifier=identifier)

        if last_designation is None:
            if glue is not None:
                last_designation, _, _ = rds_query.glue_dict[glue] #TODO: is this even correct?
            if glue is None:
                last_designation = rds_query.root
        else:
            if glue is not None:
                rds_query.glue_dict[glue] = designation, prefix, ellipsis

        rds_query.gr.add_edge(last_designation, designation, edge_type=prefix, ellipsis=ellipsis)

        return designation


    # Visit a parse tree produced by rdsqueryParser#signalExpr.
    def visitSignalExpr(self, ctx:rdsqueryParser.SignalExprContext, rds_query: RDSQuery, last_node:QueryNode, edge_type:str):
        if ctx.signal_path is not None:
            self.visitSignalPath(ctx.signal_path, rds_query, last_node, edge_type)

        if ctx.signal_cond_expr is not None:
            self.visitSignalCondExpr(ctx.signal_cond_expr, rds_query, last_node, edge_type)

    # Visit a parse tree produced by rdsqueryParser#signalCondExpr.
    def visitSignalCondExpr(self, ctx:rdsqueryParser.SignalCondExprContext, rds_query:RDSQuery, last_node:QueryNode, edge_type:str):
        lhs = self.visitSignalPath(ctx.signal_path, rds_query, last_node, edge_type)

        if ctx.literal is not None:
            if '.' in ctx.literal.text:
                rhs = float(ctx.literal.text)
            elif ctx.literal.text in {'true','false'}:
                rhs = bool(ctx.literal.text)
            else:
                rhs = int(ctx.literal.text)
        elif ctx.glued_signal_path is not None:
            rhs = self.visitGluedSignalPath(ctx.glued_signal_path, rds_query)
        else:
            raise SyntaxError('No right hand side in signal conditional expression')

        rds_query.query_filters.append(QueryFilter(lhs = lhs, op = ctx.op.text, rhs=rhs))


    # Visit a parse tree produced by rdsqueryParser#signalPath.
    def visitSignalPath(self, ctx:rdsqueryParser.SignalPathContext, rds_query:RDSQuery, last_node:QueryNode, edge_type:str):
        if ctx.glue is not None:
            glue = extract_glue(ctx.glue.text)
        else:
            glue = None

        cd = cdict(ctx)

        #ids = [c for c in s]
        for t in cd['TerminalNodeImpl']:
            if t.symbol.text == '.':
                edge_type = '.'
            elif glue is not None and t.symbol.text == ctx.glue.text:
                pass
            else:
                signal = QueryNode(t.symbol.text)
                rds_query.gr.add_edge(last_node, signal, edge_type=edge_type, ellipsis=False)
                last_node = signal

        if glue is not None:
            rds_query.glue_dict[glue] = last_node, '.', False

        return last_node

    # Visit a parse tree produced by rdsqueryParser#gluedSignalPath.
    def visitGluedSignalPath(self, ctx:rdsqueryParser.GluedSignalPathContext, rds_query:RDSQuery):
        glue = extract_glue(ctx.glue.text)

        last_node, edge_type, ellipsis = rds_query.glue_dict[glue]

        return self.visitSignalPath(ctx.signal_path, rds_query, last_node, edge_type)

    # Visit a parse tree produced by rdsqueryParser#gluedSignalExpr.
    def visitGluedSignalExpr(self, ctx:rdsqueryParser.GluedSignalExprContext, rds_query:RDSQuery):
        glue = extract_glue(ctx.glue.text)

        last_node, edge_type, ellipsis = rds_query.glue_dict[glue]

        self.visitSignalExpr(ctx.signal_expr, rds_query, last_node, edge_type)

    # Visit a parse tree produced by rdsqueryParser#dateTime.
    def visitDateTime(self, ctx:rdsqueryParser.DateTimeContext):
        return parser.parse(ctx.FULL_DATE().symbol.text + 'T' + ctx.FULL_TIME().symbol.text)


del rdsqueryParser