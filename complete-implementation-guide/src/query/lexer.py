"""
SQL Lexer (Tokenizer): converts SQL string into tokens.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """Token types for SQL."""

    # Keywords
    SELECT = auto()
    FROM = auto()
    WHERE = auto()
    INSERT = auto()
    INTO = auto()
    VALUES = auto()
    UPDATE = auto()
    SET = auto()
    DELETE = auto()
    CREATE = auto()
    TABLE = auto()
    DROP = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    NULL = auto()
    ASC = auto()
    DESC = auto()
    ORDER = auto()
    BY = auto()
    GROUP = auto()
    HAVING = auto()
    LIMIT = auto()
    OFFSET = auto()
    JOIN = auto()
    INNER = auto()
    LEFT = auto()
    RIGHT = auto()
    ON = auto()
    AS = auto()

    # Types
    INT = auto()
    VARCHAR = auto()
    FLOAT = auto()
    BOOLEAN = auto()

    # Operators
    EQ = auto()          # =
    NEQ = auto()         # !=, <>
    LT = auto()          # <
    LTE = auto()         # <=
    GT = auto()          # >
    GTE = auto()         # >=
    PLUS = auto()        # +
    MINUS = auto()       # -
    STAR = auto()        # *
    SLASH = auto()       # /

    # Punctuation
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    COMMA = auto()       # ,
    SEMICOLON = auto()   # ;
    DOT = auto()         # .

    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()

    # Special
    EOF = auto()


@dataclass
class Token:
    """Represents a single token."""
    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, '{self.value}', {self.line}:{self.column})"


class Lexer:
    """SQL lexer/tokenizer."""

    KEYWORDS = {
        'SELECT': TokenType.SELECT,
        'FROM': TokenType.FROM,
        'WHERE': TokenType.WHERE,
        'INSERT': TokenType.INSERT,
        'INTO': TokenType.INTO,
        'VALUES': TokenType.VALUES,
        'UPDATE': TokenType.UPDATE,
        'SET': TokenType.SET,
        'DELETE': TokenType.DELETE,
        'CREATE': TokenType.CREATE,
        'TABLE': TokenType.TABLE,
        'DROP': TokenType.DROP,
        'AND': TokenType.AND,
        'OR': TokenType.OR,
        'NOT': TokenType.NOT,
        'NULL': TokenType.NULL,
        'ASC': TokenType.ASC,
        'DESC': TokenType.DESC,
        'ORDER': TokenType.ORDER,
        'BY': TokenType.BY,
        'GROUP': TokenType.GROUP,
        'HAVING': TokenType.HAVING,
        'LIMIT': TokenType.LIMIT,
        'OFFSET': TokenType.OFFSET,
        'JOIN': TokenType.JOIN,
        'INNER': TokenType.INNER,
        'LEFT': TokenType.LEFT,
        'RIGHT': TokenType.RIGHT,
        'ON': TokenType.ON,
        'AS': TokenType.AS,
        'INT': TokenType.INT,
        'VARCHAR': TokenType.VARCHAR,
        'FLOAT': TokenType.FLOAT,
        'BOOLEAN': TokenType.BOOLEAN,
    }

    def __init__(self, sql: str):
        self.sql = sql
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> List[Token]:
        """Tokenize the SQL string."""
        tokens = []

        while self.pos < len(self.sql):
            # Skip whitespace
            if self._current_char().isspace():
                self._skip_whitespace()
                continue

            # Skip comments
            if self._current_char() == '-' and self._peek_char() == '-':
                self._skip_comment()
                continue

            # Numbers
            if self._current_char().isdigit():
                tokens.append(self._read_number())
                continue

            # Strings
            if self._current_char() in ('"', "'"):
                tokens.append(self._read_string())
                continue

            # Identifiers or keywords
            if self._current_char().isalpha() or self._current_char() == '_':
                tokens.append(self._read_identifier())
                continue

            # Operators and punctuation
            token = self._read_operator()
            if token:
                tokens.append(token)
                continue

            # Unknown character
            raise SyntaxError(f"Unexpected character '{self._current_char()}' at {self.line}:{self.column}")

        tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return tokens

    def _current_char(self) -> str:
        if self.pos >= len(self.sql):
            return '\0'
        return self.sql[self.pos]

    def _peek_char(self, offset: int = 1) -> str:
        pos = self.pos + offset
        if pos >= len(self.sql):
            return '\0'
        return self.sql[pos]

    def _advance(self) -> None:
        if self.pos < len(self.sql):
            if self.sql[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1

    def _skip_whitespace(self) -> None:
        while self._current_char().isspace():
            self._advance()

    def _skip_comment(self) -> None:
        while self._current_char() != '\n' and self._current_char() != '\0':
            self._advance()

    def _read_number(self) -> Token:
        start_line, start_col = self.line, self.column
        num_str = ''

        while self._current_char().isdigit() or self._current_char() == '.':
            num_str += self._current_char()
            self._advance()

        return Token(TokenType.NUMBER, num_str, start_line, start_col)

    def _read_string(self) -> Token:
        start_line, start_col = self.line, self.column
        quote = self._current_char()
        self._advance()  # Skip opening quote

        string_val = ''
        while self._current_char() != quote and self._current_char() != '\0':
            string_val += self._current_char()
            self._advance()

        if self._current_char() == quote:
            self._advance()  # Skip closing quote

        return Token(TokenType.STRING, string_val, start_line, start_col)

    def _read_identifier(self) -> Token:
        start_line, start_col = self.line, self.column
        ident = ''

        while self._current_char().isalnum() or self._current_char() == '_':
            ident += self._current_char()
            self._advance()

        # Check if keyword
        ident_upper = ident.upper()
        if ident_upper in self.KEYWORDS:
            return Token(self.KEYWORDS[ident_upper], ident_upper, start_line, start_col)

        return Token(TokenType.IDENTIFIER, ident, start_line, start_col)

    def _read_operator(self) -> Optional[Token]:
        start_line, start_col = self.line, self.column
        char = self._current_char()

        # Two-character operators
        if char == '<':
            self._advance()
            if self._current_char() == '=':
                self._advance()
                return Token(TokenType.LTE, '<=', start_line, start_col)
            elif self._current_char() == '>':
                self._advance()
                return Token(TokenType.NEQ, '<>', start_line, start_col)
            return Token(TokenType.LT, '<', start_line, start_col)

        if char == '>':
            self._advance()
            if self._current_char() == '=':
                self._advance()
                return Token(TokenType.GTE, '>=', start_line, start_col)
            return Token(TokenType.GT, '>', start_line, start_col)

        if char == '!':
            self._advance()
            if self._current_char() == '=':
                self._advance()
                return Token(TokenType.NEQ, '!=', start_line, start_col)

        # Single-character operators
        single_char_tokens = {
            '=': TokenType.EQ,
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            ',': TokenType.COMMA,
            ';': TokenType.SEMICOLON,
            '.': TokenType.DOT,
        }

        if char in single_char_tokens:
            self._advance()
            return Token(single_char_tokens[char], char, start_line, start_col)

        return None
