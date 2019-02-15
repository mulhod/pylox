from enum import Enum

token_types = []

# Single-character tokens.
token_types.extend(['LEFT_PAREN', 'RIGHT_PAREN', 'LEFT_BRACE',
                    'RIGHT_BRACE', 'COMMA', 'DOT', 'MINUS', 'PLUS',
                    'SEMICOLON', 'SLASH', 'STAR'])

# One or two character tokens.
token_types.extend(['BANG', 'BANG_EQUAL', 'EQUAL', 'EQUAL_EQUAL',
                    'GREATER', 'GREATER_EQUAL', 'LESS', 'LESS_EQUAL'])

# Literals.
token_types.extend(['IDENTIFIER', 'STRING', 'NUMBER'])

# Keywords.
token_types.extend(['AND', 'CLASS', 'ELSE', 'FALSE', 'FUN', 'FOR',
                    'IF', 'NIL', 'OR', 'PRINT', 'RETURN', 'SUPER',
                    'THIS', 'TRUE', 'VAR', 'WHILE'])

token_types.append('EOF')

TokenType = Enum('TokenType', ' '.join(token_types))
