# Generated from rdsquery.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .rdsqueryParser import rdsqueryParser
else:
    from rdsqueryParser import rdsqueryParser

# This class defines a complete listener for a parse tree produced by rdsqueryParser.
class rdsqueryListener(ParseTreeListener):

    # Enter a parse tree produced by rdsqueryParser#rdsQuery.
    def enterRdsQuery(self, ctx:rdsqueryParser.RdsQueryContext):
        pass

    # Exit a parse tree produced by rdsqueryParser#rdsQuery.
    def exitRdsQuery(self, ctx:rdsqueryParser.RdsQueryContext):
        pass


    # Enter a parse tree produced by rdsqueryParser#queryExpression.
    def enterQueryExpression(self, ctx:rdsqueryParser.QueryExpressionContext):
        pass

    # Exit a parse tree produced by rdsqueryParser#queryExpression.
    def exitQueryExpression(self, ctx:rdsqueryParser.QueryExpressionContext):
        pass


    # Enter a parse tree produced by rdsqueryParser#designationExpr.
    def enterDesignationExpr(self, ctx:rdsqueryParser.DesignationExprContext):
        pass

    # Exit a parse tree produced by rdsqueryParser#designationExpr.
    def exitDesignationExpr(self, ctx:rdsqueryParser.DesignationExprContext):
        pass


    # Enter a parse tree produced by rdsqueryParser#singleDesignation.
    def enterSingleDesignation(self, ctx:rdsqueryParser.SingleDesignationContext):
        pass

    # Exit a parse tree produced by rdsqueryParser#singleDesignation.
    def exitSingleDesignation(self, ctx:rdsqueryParser.SingleDesignationContext):
        pass


    # Enter a parse tree produced by rdsqueryParser#aspectPrefix.
    def enterAspectPrefix(self, ctx:rdsqueryParser.AspectPrefixContext):
        pass

    # Exit a parse tree produced by rdsqueryParser#aspectPrefix.
    def exitAspectPrefix(self, ctx:rdsqueryParser.AspectPrefixContext):
        pass


    # Enter a parse tree produced by rdsqueryParser#signalExpr.
    def enterSignalExpr(self, ctx:rdsqueryParser.SignalExprContext):
        pass

    # Exit a parse tree produced by rdsqueryParser#signalExpr.
    def exitSignalExpr(self, ctx:rdsqueryParser.SignalExprContext):
        pass


    # Enter a parse tree produced by rdsqueryParser#signalCondExpr.
    def enterSignalCondExpr(self, ctx:rdsqueryParser.SignalCondExprContext):
        pass

    # Exit a parse tree produced by rdsqueryParser#signalCondExpr.
    def exitSignalCondExpr(self, ctx:rdsqueryParser.SignalCondExprContext):
        pass


    # Enter a parse tree produced by rdsqueryParser#signalPath.
    def enterSignalPath(self, ctx:rdsqueryParser.SignalPathContext):
        pass

    # Exit a parse tree produced by rdsqueryParser#signalPath.
    def exitSignalPath(self, ctx:rdsqueryParser.SignalPathContext):
        pass


    # Enter a parse tree produced by rdsqueryParser#gluedSignalPath.
    def enterGluedSignalPath(self, ctx:rdsqueryParser.GluedSignalPathContext):
        pass

    # Exit a parse tree produced by rdsqueryParser#gluedSignalPath.
    def exitGluedSignalPath(self, ctx:rdsqueryParser.GluedSignalPathContext):
        pass


    # Enter a parse tree produced by rdsqueryParser#gluedSignalExpr.
    def enterGluedSignalExpr(self, ctx:rdsqueryParser.GluedSignalExprContext):
        pass

    # Exit a parse tree produced by rdsqueryParser#gluedSignalExpr.
    def exitGluedSignalExpr(self, ctx:rdsqueryParser.GluedSignalExprContext):
        pass


    # Enter a parse tree produced by rdsqueryParser#dateTime.
    def enterDateTime(self, ctx:rdsqueryParser.DateTimeContext):
        pass

    # Exit a parse tree produced by rdsqueryParser#dateTime.
    def exitDateTime(self, ctx:rdsqueryParser.DateTimeContext):
        pass



del rdsqueryParser