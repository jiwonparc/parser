""" Test the specification parser

"""

import logging
import unittest

from io import StringIO

from ply.lex import LexToken
import ply.yacc as yacc

from parser import lexer, reset, parser


class TestLexer(unittest.TestCase):
    def setUp(self):
        # Run before every test
        reset()

    @staticmethod
    def new_tok(lexpos, tok_type, lineno, value):
        # Create a token
        tok = LexToken()
        tok.value = value
        tok.lineno = lineno
        tok.lexpos = lexpos
        tok.type = tok_type
        return tok

    def _test_multiple_token(self, token_list, string):
        # clean the lexer state
        # for f in lexer: None
        lexer.input(string)

        i = 0
        tok = lexer.token()
        while (tok is not None):
            if i > len(token_list):
                raise Exception("Found more tokens than expeced")
            self.assertTrue(tok.value == token_list[i].value)
            self.assertTrue(tok.lineno == token_list[i].lineno)
            self.assertTrue(tok.lexpos == token_list[i].lexpos)
            self.assertTrue(tok.type == token_list[i].type)

            i = i + 1
            tok = lexer.token()

        # did not parse anything else
        with self.assertRaises(StopIteration):
            lexer.next()


    def _test_single_token(self, lexpos, tok_type, lineno, value, string):
        """ Test if the lexer reads correctly a token from string.

        - lexpos, tok_type, lineno, value define a token
        - string is the input string to the lexer

        The method test if lexer(string) = new_token(lexpos, tok_type, lineno, value).
        """
        tok_ref = TestLexer.new_tok(lexpos,tok_type,lineno,value)
        return self._test_multiple_token([tok_ref], string)


    def test_lexer(self):
        # ID regexp (from https://github.com/LS-Lab/KeYmaeraX-release/blob/master/keymaerax-core/src/main/scala/edu/cmu/cs/ls/keymaerax/parser/KeYmaeraXLexer.scala)
        # ([a-zA-Z][a-zA-Z0-9]*\_?\_?[0-9]*)
        self._test_single_token(0,'ID',1,'x','x')
        self._test_single_token(0,'ID',1,'aabzA','aabzA')
        self._test_single_token(0,'ID',1,'a04','a04')
        self._test_single_token(0,'ID',1,'a04Az','a04Az')
        self._test_single_token(0,'ID',1,'a04Az_95','a04Az_95')

        self._test_single_token(0,'TRUE',1,'True','True')


        self._test_single_token(0,'OR',1,'|','|')
        self._test_single_token(0,'AND',1,'&','&')


class TestParser(unittest.TestCase):
    def setUp(self):
        # Run before every test
        reset()

    def test_expressions(self):
        def _must_fail(parser, string):
            """ Parsing must fail, not a valid expression """
            with self.assertRaises(TypeError):
                parse_res = parser.parse(string)

        def _must_be_eq(parser, string, expected):
            parse_res = parser.parse(string)

            if (parse_res != expected):
                print("Found: %s\nInstead of: %s" % (str(parse_res), str(expected)))

            self.assertTrue(parse_res == expected)


        _must_be_eq(parser, "x & y", ('&', ("IDENTIFIER", 'x'), ("IDENTIFIER", 'y')))

        # Not a complete expression - parsing must fail
        _must_fail(parser, "true + false")
