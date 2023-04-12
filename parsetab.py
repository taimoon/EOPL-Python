
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = "BEGIN CAR CDR COND CONS DEREF ELSE END EQUAL_TEST GREATER_TEST ID IF IN LESS_TEST LET LETREC LET_STAR LIST MINUS NEWREF NULL NUMBER PROC RIGHTARROW SET THEN UNPACK ZERO_TESTexpr : '(' expr_list ')'expr_list : expr\n                 | expr expr_listexpr : PROC '(' params_opt ')' exprparams_opt : \n            | paramsparams : ID\n              | ID ',' paramsexpr : NUMBERexpr : IDexpr : NULL\n    expr : ZERO_TEST '(' expr ')'\n         | MINUS '(' expr ')'\n         | CAR '(' expr ')'\n         | CDR '(' expr ')'\n    expr : '-' '(' expr ',' expr ')'\n            | '+' '(' expr ',' expr ')'\n            | '*' '(' expr ',' expr ')'\n            | '/' '(' expr ',' expr ')'\n            | GREATER_TEST '(' expr ',' expr ')'\n            | LESS_TEST '(' expr ',' expr ')'\n            | EQUAL_TEST '(' expr ',' expr ')'\n            | CONS '(' expr ',' expr ')' \n            | '-' expr\n        \n    expr : LIST '(' list_opt ')'\n    list_opt : \n              | list_vals list_vals : expr\n                | expr ',' list_valsexpr : IF expr THEN expr ELSE exprexpr : UNPACK vars '=' expr IN exprvars : ID\n              | ID vars    expr : BEGIN expr_seq    expr_seq : expr END\n            | expr ';' expr_seq\n            expr : LET let_pairs IN expr\n    let_pairs : let_pair\n                | let_pair let_pairslet_pair : ID '=' expr expr : LET_STAR let_pairs IN exprexpr : LETREC letrec_pairs IN expr\n    letrec_pairs : letrec_pair\n                | letrec_pair letrec_pairsletrec_pair : ID '(' params_opt ')' '=' exprexpr : COND cond_clauses ENDcond_clauses : cond_clause\n                    | cond_clause ELSE expr\n                    | cond_clause cond_clausescond_clause : expr RIGHTARROW expr    expr : NEWREF '(' expr ')'\n        | DEREF '(' expr ')'\n        | SET '(' expr ',' expr ')'\n    "
    
_lr_action_items = {'(':([0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,22,26,27,28,29,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,58,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[2,2,32,-9,-10,-11,33,34,35,36,37,39,40,41,42,43,44,45,46,2,2,2,62,63,64,2,2,2,2,2,2,-24,2,2,2,2,2,2,2,2,-34,96,2,2,2,2,-1,2,2,2,-35,2,2,2,2,2,-46,2,2,2,-12,-13,-14,-15,2,2,2,2,2,2,2,2,-25,2,-36,-37,-41,-42,-50,-51,-52,2,-4,2,2,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,2,-53,]),'PROC':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[3,3,-9,-10,-11,3,3,3,3,3,3,3,3,3,3,-24,3,3,3,3,3,3,3,3,-34,3,3,3,3,-1,3,3,3,-35,3,3,3,3,3,-46,3,3,3,-12,-13,-14,-15,3,3,3,3,3,3,3,3,-25,3,-36,-37,-41,-42,-50,-51,-52,3,-4,3,3,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,3,-53,]),'NUMBER':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[4,4,-9,-10,-11,4,4,4,4,4,4,4,4,4,4,-24,4,4,4,4,4,4,4,4,-34,4,4,4,4,-1,4,4,4,-35,4,4,4,4,4,-46,4,4,4,-12,-13,-14,-15,4,4,4,4,4,4,4,4,-25,4,-36,-37,-41,-42,-50,-51,-52,4,-4,4,4,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,4,-53,]),'ID':([0,2,4,5,6,11,20,21,22,23,24,25,26,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,49,50,53,57,60,62,63,64,65,74,85,86,88,89,90,92,93,94,96,97,98,100,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,124,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,160,],[5,5,-9,-10,-11,5,5,49,5,54,54,58,5,5,69,5,5,5,5,5,-24,5,5,5,5,5,5,5,5,49,-34,54,58,5,5,5,5,-1,5,5,5,-35,5,5,5,5,5,69,-46,5,5,5,69,-12,-13,-14,-15,5,5,5,5,5,5,5,5,-25,5,-36,-37,-40,-41,-42,-50,-51,-52,5,-4,5,5,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,5,-53,-45,]),'NULL':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[6,6,-9,-10,-11,6,6,6,6,6,6,6,6,6,6,-24,6,6,6,6,6,6,6,6,-34,6,6,6,6,-1,6,6,6,-35,6,6,6,6,6,-46,6,6,6,-12,-13,-14,-15,6,6,6,6,6,6,6,6,-25,6,-36,-37,-41,-42,-50,-51,-52,6,-4,6,6,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,6,-53,]),'ZERO_TEST':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[7,7,-9,-10,-11,7,7,7,7,7,7,7,7,7,7,-24,7,7,7,7,7,7,7,7,-34,7,7,7,7,-1,7,7,7,-35,7,7,7,7,7,-46,7,7,7,-12,-13,-14,-15,7,7,7,7,7,7,7,7,-25,7,-36,-37,-41,-42,-50,-51,-52,7,-4,7,7,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,7,-53,]),'MINUS':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[8,8,-9,-10,-11,8,8,8,8,8,8,8,8,8,8,-24,8,8,8,8,8,8,8,8,-34,8,8,8,8,-1,8,8,8,-35,8,8,8,8,8,-46,8,8,8,-12,-13,-14,-15,8,8,8,8,8,8,8,8,-25,8,-36,-37,-41,-42,-50,-51,-52,8,-4,8,8,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,8,-53,]),'CAR':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[9,9,-9,-10,-11,9,9,9,9,9,9,9,9,9,9,-24,9,9,9,9,9,9,9,9,-34,9,9,9,9,-1,9,9,9,-35,9,9,9,9,9,-46,9,9,9,-12,-13,-14,-15,9,9,9,9,9,9,9,9,-25,9,-36,-37,-41,-42,-50,-51,-52,9,-4,9,9,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,9,-53,]),'CDR':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[10,10,-9,-10,-11,10,10,10,10,10,10,10,10,10,10,-24,10,10,10,10,10,10,10,10,-34,10,10,10,10,-1,10,10,10,-35,10,10,10,10,10,-46,10,10,10,-12,-13,-14,-15,10,10,10,10,10,10,10,10,-25,10,-36,-37,-41,-42,-50,-51,-52,10,-4,10,10,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,10,-53,]),'-':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[11,11,-9,-10,-11,11,11,11,11,11,11,11,11,11,11,-24,11,11,11,11,11,11,11,11,-34,11,11,11,11,-1,11,11,11,-35,11,11,11,11,11,-46,11,11,11,-12,-13,-14,-15,11,11,11,11,11,11,11,11,-25,11,-36,-37,-41,-42,-50,-51,-52,11,-4,11,11,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,11,-53,]),'+':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[12,12,-9,-10,-11,12,12,12,12,12,12,12,12,12,12,-24,12,12,12,12,12,12,12,12,-34,12,12,12,12,-1,12,12,12,-35,12,12,12,12,12,-46,12,12,12,-12,-13,-14,-15,12,12,12,12,12,12,12,12,-25,12,-36,-37,-41,-42,-50,-51,-52,12,-4,12,12,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,12,-53,]),'*':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[13,13,-9,-10,-11,13,13,13,13,13,13,13,13,13,13,-24,13,13,13,13,13,13,13,13,-34,13,13,13,13,-1,13,13,13,-35,13,13,13,13,13,-46,13,13,13,-12,-13,-14,-15,13,13,13,13,13,13,13,13,-25,13,-36,-37,-41,-42,-50,-51,-52,13,-4,13,13,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,13,-53,]),'/':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[14,14,-9,-10,-11,14,14,14,14,14,14,14,14,14,14,-24,14,14,14,14,14,14,14,14,-34,14,14,14,14,-1,14,14,14,-35,14,14,14,14,14,-46,14,14,14,-12,-13,-14,-15,14,14,14,14,14,14,14,14,-25,14,-36,-37,-41,-42,-50,-51,-52,14,-4,14,14,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,14,-53,]),'GREATER_TEST':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[15,15,-9,-10,-11,15,15,15,15,15,15,15,15,15,15,-24,15,15,15,15,15,15,15,15,-34,15,15,15,15,-1,15,15,15,-35,15,15,15,15,15,-46,15,15,15,-12,-13,-14,-15,15,15,15,15,15,15,15,15,-25,15,-36,-37,-41,-42,-50,-51,-52,15,-4,15,15,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,15,-53,]),'LESS_TEST':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[16,16,-9,-10,-11,16,16,16,16,16,16,16,16,16,16,-24,16,16,16,16,16,16,16,16,-34,16,16,16,16,-1,16,16,16,-35,16,16,16,16,16,-46,16,16,16,-12,-13,-14,-15,16,16,16,16,16,16,16,16,-25,16,-36,-37,-41,-42,-50,-51,-52,16,-4,16,16,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,16,-53,]),'EQUAL_TEST':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[17,17,-9,-10,-11,17,17,17,17,17,17,17,17,17,17,-24,17,17,17,17,17,17,17,17,-34,17,17,17,17,-1,17,17,17,-35,17,17,17,17,17,-46,17,17,17,-12,-13,-14,-15,17,17,17,17,17,17,17,17,-25,17,-36,-37,-41,-42,-50,-51,-52,17,-4,17,17,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,17,-53,]),'CONS':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[18,18,-9,-10,-11,18,18,18,18,18,18,18,18,18,18,-24,18,18,18,18,18,18,18,18,-34,18,18,18,18,-1,18,18,18,-35,18,18,18,18,18,-46,18,18,18,-12,-13,-14,-15,18,18,18,18,18,18,18,18,-25,18,-36,-37,-41,-42,-50,-51,-52,18,-4,18,18,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,18,-53,]),'LIST':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[19,19,-9,-10,-11,19,19,19,19,19,19,19,19,19,19,-24,19,19,19,19,19,19,19,19,-34,19,19,19,19,-1,19,19,19,-35,19,19,19,19,19,-46,19,19,19,-12,-13,-14,-15,19,19,19,19,19,19,19,19,-25,19,-36,-37,-41,-42,-50,-51,-52,19,-4,19,19,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,19,-53,]),'IF':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[20,20,-9,-10,-11,20,20,20,20,20,20,20,20,20,20,-24,20,20,20,20,20,20,20,20,-34,20,20,20,20,-1,20,20,20,-35,20,20,20,20,20,-46,20,20,20,-12,-13,-14,-15,20,20,20,20,20,20,20,20,-25,20,-36,-37,-41,-42,-50,-51,-52,20,-4,20,20,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,20,-53,]),'UNPACK':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[21,21,-9,-10,-11,21,21,21,21,21,21,21,21,21,21,-24,21,21,21,21,21,21,21,21,-34,21,21,21,21,-1,21,21,21,-35,21,21,21,21,21,-46,21,21,21,-12,-13,-14,-15,21,21,21,21,21,21,21,21,-25,21,-36,-37,-41,-42,-50,-51,-52,21,-4,21,21,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,21,-53,]),'BEGIN':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[22,22,-9,-10,-11,22,22,22,22,22,22,22,22,22,22,-24,22,22,22,22,22,22,22,22,-34,22,22,22,22,-1,22,22,22,-35,22,22,22,22,22,-46,22,22,22,-12,-13,-14,-15,22,22,22,22,22,22,22,22,-25,22,-36,-37,-41,-42,-50,-51,-52,22,-4,22,22,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,22,-53,]),'LET':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[23,23,-9,-10,-11,23,23,23,23,23,23,23,23,23,23,-24,23,23,23,23,23,23,23,23,-34,23,23,23,23,-1,23,23,23,-35,23,23,23,23,23,-46,23,23,23,-12,-13,-14,-15,23,23,23,23,23,23,23,23,-25,23,-36,-37,-41,-42,-50,-51,-52,23,-4,23,23,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,23,-53,]),'LET_STAR':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[24,24,-9,-10,-11,24,24,24,24,24,24,24,24,24,24,-24,24,24,24,24,24,24,24,24,-34,24,24,24,24,-1,24,24,24,-35,24,24,24,24,24,-46,24,24,24,-12,-13,-14,-15,24,24,24,24,24,24,24,24,-25,24,-36,-37,-41,-42,-50,-51,-52,24,-4,24,24,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,24,-53,]),'LETREC':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[25,25,-9,-10,-11,25,25,25,25,25,25,25,25,25,25,-24,25,25,25,25,25,25,25,25,-34,25,25,25,25,-1,25,25,25,-35,25,25,25,25,25,-46,25,25,25,-12,-13,-14,-15,25,25,25,25,25,25,25,25,-25,25,-36,-37,-41,-42,-50,-51,-52,25,-4,25,25,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,25,-53,]),'COND':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[26,26,-9,-10,-11,26,26,26,26,26,26,26,26,26,26,-24,26,26,26,26,26,26,26,26,-34,26,26,26,26,-1,26,26,26,-35,26,26,26,26,26,-46,26,26,26,-12,-13,-14,-15,26,26,26,26,26,26,26,26,-25,26,-36,-37,-41,-42,-50,-51,-52,26,-4,26,26,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,26,-53,]),'NEWREF':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[27,27,-9,-10,-11,27,27,27,27,27,27,27,27,27,27,-24,27,27,27,27,27,27,27,27,-34,27,27,27,27,-1,27,27,27,-35,27,27,27,27,27,-46,27,27,27,-12,-13,-14,-15,27,27,27,27,27,27,27,27,-25,27,-36,-37,-41,-42,-50,-51,-52,27,-4,27,27,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,27,-53,]),'DEREF':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[28,28,-9,-10,-11,28,28,28,28,28,28,28,28,28,28,-24,28,28,28,28,28,28,28,28,-34,28,28,28,28,-1,28,28,28,-35,28,28,28,28,28,-46,28,28,28,-12,-13,-14,-15,28,28,28,28,28,28,28,28,-25,28,-36,-37,-41,-42,-50,-51,-52,28,-4,28,28,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,28,-53,]),'SET':([0,2,4,5,6,11,20,22,26,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,50,60,62,63,64,65,74,85,86,88,89,90,92,93,94,97,98,100,104,106,107,108,109,110,111,112,113,114,115,116,117,118,119,122,123,125,126,129,130,131,132,133,144,145,148,149,150,151,152,153,154,155,156,157,158,159,],[29,29,-9,-10,-11,29,29,29,29,29,29,29,29,29,29,-24,29,29,29,29,29,29,29,29,-34,29,29,29,29,-1,29,29,29,-35,29,29,29,29,29,-46,29,29,29,-12,-13,-14,-15,29,29,29,29,29,29,29,29,-25,29,-36,-37,-41,-42,-50,-51,-52,29,-4,29,29,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,29,-53,]),'$end':([1,4,5,6,38,50,65,88,97,106,107,108,109,118,122,123,125,126,130,131,133,148,149,150,151,152,153,154,155,156,157,159,],[0,-9,-10,-11,-24,-34,-1,-35,-46,-12,-13,-14,-15,-25,-36,-37,-41,-42,-51,-52,-4,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,-53,]),')':([4,5,6,30,31,32,38,46,50,65,66,67,68,69,70,71,72,73,74,82,83,84,88,96,97,101,102,106,107,108,109,118,122,123,125,126,127,130,131,133,134,135,136,137,138,139,140,141,142,143,147,148,149,150,151,152,153,154,155,156,157,159,],[-9,-10,-11,65,-2,-5,-24,-26,-34,-1,-3,104,-6,-7,106,107,108,109,-2,118,-27,-28,-35,-5,-46,130,131,-12,-13,-14,-15,-25,-36,-37,-41,-42,146,-51,-52,-4,-8,148,149,150,151,152,153,154,155,-29,159,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,-53,]),'THEN':([4,5,6,38,47,50,65,88,97,106,107,108,109,118,122,123,125,126,130,131,133,148,149,150,151,152,153,154,155,156,157,159,],[-9,-10,-11,-24,85,-34,-1,-35,-46,-12,-13,-14,-15,-25,-36,-37,-41,-42,-51,-52,-4,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,-53,]),'END':([4,5,6,38,50,51,59,60,65,88,97,99,106,107,108,109,118,122,123,125,126,128,129,130,131,133,148,149,150,151,152,153,154,155,156,157,159,],[-9,-10,-11,-24,-34,88,97,-47,-1,-35,-46,-49,-12,-13,-14,-15,-25,-36,-37,-41,-42,-48,-50,-51,-52,-4,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,-53,]),';':([4,5,6,38,50,51,65,88,97,106,107,108,109,118,122,123,125,126,130,131,133,148,149,150,151,152,153,154,155,156,157,159,],[-9,-10,-11,-24,-34,89,-1,-35,-46,-12,-13,-14,-15,-25,-36,-37,-41,-42,-51,-52,-4,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,-53,]),'RIGHTARROW':([4,5,6,38,50,61,65,88,97,106,107,108,109,118,122,123,125,126,130,131,133,148,149,150,151,152,153,154,155,156,157,159,],[-9,-10,-11,-24,-34,100,-1,-35,-46,-12,-13,-14,-15,-25,-36,-37,-41,-42,-51,-52,-4,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,-53,]),',':([4,5,6,38,50,65,69,74,75,76,77,78,79,80,81,84,88,97,103,106,107,108,109,118,122,123,125,126,130,131,133,148,149,150,151,152,153,154,155,156,157,159,],[-9,-10,-11,-24,-34,-1,105,110,111,112,113,114,115,116,117,119,-35,-46,132,-12,-13,-14,-15,-25,-36,-37,-41,-42,-51,-52,-4,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,-53,]),'ELSE':([4,5,6,38,50,60,65,88,97,106,107,108,109,118,120,122,123,125,126,129,130,131,133,148,149,150,151,152,153,154,155,156,157,159,],[-9,-10,-11,-24,-34,98,-1,-35,-46,-12,-13,-14,-15,-25,144,-36,-37,-41,-42,-50,-51,-52,-4,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,-53,]),'IN':([4,5,6,38,50,52,53,55,56,57,65,88,91,95,97,106,107,108,109,118,121,122,123,124,125,126,130,131,133,148,149,150,151,152,153,154,155,156,157,159,160,],[-9,-10,-11,-24,-34,90,-38,93,94,-43,-1,-35,-39,-44,-46,-12,-13,-14,-15,-25,145,-36,-37,-40,-41,-42,-51,-52,-4,-16,-17,-18,-19,-20,-21,-22,-23,-30,-31,-53,-45,]),'=':([48,49,54,87,146,],[86,-32,92,-33,158,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'expr':([0,2,11,20,22,26,31,33,34,35,36,37,39,40,41,42,43,44,45,46,60,62,63,64,74,85,86,89,90,92,93,94,98,100,104,110,111,112,113,114,115,116,117,119,132,144,145,158,],[1,31,38,47,51,61,31,70,71,72,73,74,75,76,77,78,79,80,81,84,61,101,102,103,31,120,121,51,123,124,125,126,128,129,133,135,136,137,138,139,140,141,142,84,147,156,157,160,]),'expr_list':([2,31,37,74,],[30,66,30,66,]),'vars':([21,49,],[48,87,]),'expr_seq':([22,89,],[50,122,]),'let_pairs':([23,24,53,],[52,55,91,]),'let_pair':([23,24,53,],[53,53,53,]),'letrec_pairs':([25,57,],[56,95,]),'letrec_pair':([25,57,],[57,57,]),'cond_clauses':([26,60,],[59,99,]),'cond_clause':([26,60,],[60,60,]),'params_opt':([32,96,],[67,127,]),'params':([32,96,105,],[68,68,134,]),'list_opt':([46,],[82,]),'list_vals':([46,119,],[83,143,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> expr","S'",1,None,None,None),
  ('expr -> ( expr_list )','expr',3,'p_application','LET_parser.py',7),
  ('expr_list -> expr','expr_list',1,'p_expr_list','LET_parser.py',11),
  ('expr_list -> expr expr_list','expr_list',2,'p_expr_list','LET_parser.py',12),
  ('expr -> PROC ( params_opt ) expr','expr',5,'p_proc','LET_parser.py',18),
  ('params_opt -> <empty>','params_opt',0,'p_params_opt','LET_parser.py',22),
  ('params_opt -> params','params_opt',1,'p_params_opt','LET_parser.py',23),
  ('params -> ID','params',1,'p_params','LET_parser.py',29),
  ('params -> ID , params','params',3,'p_params','LET_parser.py',30),
  ('expr -> NUMBER','expr',1,'p_number','LET_parser.py',36),
  ('expr -> ID','expr',1,'p_var','LET_parser.py',40),
  ('expr -> NULL','expr',1,'p_null','LET_parser.py',44),
  ('expr -> ZERO_TEST ( expr )','expr',4,'p_unary_exp','LET_parser.py',49),
  ('expr -> MINUS ( expr )','expr',4,'p_unary_exp','LET_parser.py',50),
  ('expr -> CAR ( expr )','expr',4,'p_unary_exp','LET_parser.py',51),
  ('expr -> CDR ( expr )','expr',4,'p_unary_exp','LET_parser.py',52),
  ('expr -> - ( expr , expr )','expr',6,'p_bi_exp','LET_parser.py',64),
  ('expr -> + ( expr , expr )','expr',6,'p_bi_exp','LET_parser.py',65),
  ('expr -> * ( expr , expr )','expr',6,'p_bi_exp','LET_parser.py',66),
  ('expr -> / ( expr , expr )','expr',6,'p_bi_exp','LET_parser.py',67),
  ('expr -> GREATER_TEST ( expr , expr )','expr',6,'p_bi_exp','LET_parser.py',68),
  ('expr -> LESS_TEST ( expr , expr )','expr',6,'p_bi_exp','LET_parser.py',69),
  ('expr -> EQUAL_TEST ( expr , expr )','expr',6,'p_bi_exp','LET_parser.py',70),
  ('expr -> CONS ( expr , expr )','expr',6,'p_bi_exp','LET_parser.py',71),
  ('expr -> - expr','expr',2,'p_bi_exp','LET_parser.py',72),
  ('expr -> LIST ( list_opt )','expr',4,'p_list_exp','LET_parser.py',96),
  ('list_opt -> <empty>','list_opt',0,'p_list_opt','LET_parser.py',103),
  ('list_opt -> list_vals','list_opt',1,'p_list_opt','LET_parser.py',104),
  ('list_vals -> expr','list_vals',1,'p_list_vals','LET_parser.py',110),
  ('list_vals -> expr , list_vals','list_vals',3,'p_list_vals','LET_parser.py',111),
  ('expr -> IF expr THEN expr ELSE expr','expr',6,'p_branch','LET_parser.py',117),
  ('expr -> UNPACK vars = expr IN expr','expr',6,'p_unpack_exp','LET_parser.py',121),
  ('vars -> ID','vars',1,'p_unpack_vars','LET_parser.py',127),
  ('vars -> ID vars','vars',2,'p_unpack_vars','LET_parser.py',128),
  ('expr -> BEGIN expr_seq','expr',2,'p_sequence','LET_parser.py',134),
  ('expr_seq -> expr END','expr_seq',2,'p_expr_seq','LET_parser.py',140),
  ('expr_seq -> expr ; expr_seq','expr_seq',3,'p_expr_seq','LET_parser.py',141),
  ('expr -> LET let_pairs IN expr','expr',4,'p_let_exp','LET_parser.py',151),
  ('let_pairs -> let_pair','let_pairs',1,'p_let_pairs','LET_parser.py',159),
  ('let_pairs -> let_pair let_pairs','let_pairs',2,'p_let_pairs','LET_parser.py',160),
  ('let_pair -> ID = expr','let_pair',3,'p_let_pair','LET_parser.py',169),
  ('expr -> LET_STAR let_pairs IN expr','expr',4,'p_let_star_exp','LET_parser.py',173),
  ('expr -> LETREC letrec_pairs IN expr','expr',4,'p_letrec_exp','LET_parser.py',192),
  ('letrec_pairs -> letrec_pair','letrec_pairs',1,'p_letrec_pairs','LET_parser.py',202),
  ('letrec_pairs -> letrec_pair letrec_pairs','letrec_pairs',2,'p_letrec_pairs','LET_parser.py',203),
  ('letrec_pair -> ID ( params_opt ) = expr','letrec_pair',6,'p_letrec_pair','LET_parser.py',209),
  ('expr -> COND cond_clauses END','expr',3,'p_cond_exp','LET_parser.py',213),
  ('cond_clauses -> cond_clause','cond_clauses',1,'p_clauses_expand','LET_parser.py',221),
  ('cond_clauses -> cond_clause ELSE expr','cond_clauses',3,'p_clauses_expand','LET_parser.py',222),
  ('cond_clauses -> cond_clause cond_clauses','cond_clauses',2,'p_clauses_expand','LET_parser.py',223),
  ('cond_clause -> expr RIGHTARROW expr','cond_clause',3,'p_clause_exp','LET_parser.py',233),
  ('expr -> NEWREF ( expr )','expr',4,'p_memory_exp','LET_parser.py',237),
  ('expr -> DEREF ( expr )','expr',4,'p_memory_exp','LET_parser.py',238),
  ('expr -> SET ( expr , expr )','expr',6,'p_memory_exp','LET_parser.py',239),
]
