//Copyright 2021 Prediktor AS
//
//Licensed under the Apache License, Version 2.0 (the "License");
//you may not use this file except in compliance with the License.
//You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
//Unless required by applicable law or agreed to in writing, software
//distributed under the License is distributed on an "AS IS" BASIS,
//WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//See the License for the specific language governing permissions and
//limitations under the License.

grammar rdsquery;
options {language=Python3;}

rdsQuery :
  queryExpression+ ('from ' fromdt=dateTime) ('to ' todt=dateTime)
  ;

queryExpression :
  designationExpr
  | gluedSignalExpr
  ;

designationExpr : singleDesignation+ '/' signal_expr=signalExpr?
  ;

singleDesignation :
  prefix=aspectPrefix
  ellipsis='...'? (identifier=ID | glue=GLUE identifier=ID?)
  ;

aspectPrefix :
 ('='+ | '-'+ | '+'+ | '#'+)
 ;

signalExpr : signal_path=signalPath | signal_cond_expr=signalCondExpr ;

signalCondExpr :
  signal_path=signalPath
  ' '* //Perhaps not ideal
  (op='=' | op='>' | op='<' | op='>=' | op='<=' | op='!=')
  ' '* //Perhaps not ideal
  (glued_signal_path=gluedSignalPath | literal=LITERAL)
  ;

signalPath : (ID '.')* (ID | glue=GLUE);

gluedSignalPath : glue=GLUE signal_path=signalPath;
gluedSignalExpr : glue=GLUE signal_expr=signalExpr;

GLUE : '[' [0-9]+ ']';

//Adapted from: https://gist.github.com/jdegoes/5853435
//License is not defined for this gist
dateTime : FULL_DATE ' ' FULL_TIME;

fragment
DATE_FULL_YEAR : DIGIT DIGIT DIGIT DIGIT;

fragment
DATE_MONTH : DIGIT DIGIT;

fragment
DATE_M_DAY  : DIGIT DIGIT;

fragment
TIME_HOUR : DIGIT DIGIT;

fragment
TIME_MINUTE : DIGIT DIGIT;

fragment
TIME_SECOND: DIGIT DIGIT;

fragment
TIME_SEC_FRAC : '.' DIGIT+;

fragment
TIME_NUM_OFFSET : ('+' | '-') TIME_HOUR ':' TIME_MINUTE;

TIME_OFFSET: 'Z' | TIME_NUM_OFFSET;
PARTIAL_TIME : TIME_HOUR ':' TIME_MINUTE ':' TIME_SECOND TIME_SEC_FRAC?;
FULL_DATE : DATE_FULL_YEAR '-' DATE_MONTH '-' DATE_M_DAY;
FULL_TIME : PARTIAL_TIME TIME_OFFSET;

fragment
DIGIT : [0-9];

LITERAL : REAL | INTEGER | BOOLEAN ;
REAL : [0-9]+ '.' [0-9]+;
INTEGER : DIGIT+;
BOOLEAN : 'true' | 'false' ; //TODO fix possible bug where ID=true/false

ID : [A-Za-z]+ [0-9]*;

WS  :  (
	' '|
	'\r'|
	'\t'
	|'\u000C'
	|'\n'
	) -> skip
    ;
