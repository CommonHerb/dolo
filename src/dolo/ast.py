from __future__ import annotations

from dataclasses import dataclass

from .tokens import Token


@dataclass(frozen=True)
class Expr:
    tokens: tuple[Token, ...]


@dataclass(frozen=True)
class Param:
    name: str
    type_name: str | None = None
    type_token: Token | None = None


@dataclass(frozen=True)
class RecordDecl:
    name: str
    fields: tuple[str, ...]


@dataclass(frozen=True)
class LetStmt:
    name: str
    expr: Expr


@dataclass(frozen=True)
class AssignStmt:
    name: str
    expr: Expr
    name_token: Token | None = None


@dataclass(frozen=True)
class ReturnStmt:
    expr: Expr


@dataclass(frozen=True)
class IfStmt:
    condition: Expr
    then_body: tuple[Stmt, ...]
    else_body: tuple[Stmt, ...] = ()


Stmt = LetStmt | AssignStmt | ReturnStmt | IfStmt


@dataclass(frozen=True)
class FunctionDecl:
    name: str
    params: tuple[Param, ...]
    body: tuple[Stmt, ...]


@dataclass(frozen=True)
class Program:
    records: tuple[RecordDecl, ...]
    functions: tuple[FunctionDecl, ...]
