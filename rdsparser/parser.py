import antlr4

from .rdsqueryLexer import rdsqueryLexer
from .rdsqueryParser import rdsqueryParser
from .rdsqueryVisitor import rdsqueryVisitor

def parse_rdsquery(qstr: str):
    istream = antlr4.InputStream(qstr)
    lexer = rdsqueryLexer(istream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = rdsqueryParser(stream)
    tree = parser.rdsQuery()
    v = rdsqueryVisitor()
    query = v.visitRdsQuery(tree)
    return query
