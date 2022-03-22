#!/usr/bin/env python3
#
# LOPEZ Aliaume
#
# On an idea of Thomas Colcombet

from dataclasses import dataclass
from typing import List, Union, Dict, Optional
import itertools


def indent(string):
    return "\n".join(f"\t{x}" for x in string.splitlines())


@dataclass
class Pos:

    filepath: str
    line: int
    col: int

    def __add__(self, other):
        if isinstance(other, int):
            return Pos(self.filepath, self.line, self.col + other)
        else:
            raise ValueError(f"Cannot add {type(other)} with Pos in {self} + {other}")


@dataclass
class Line:
    line: str
    pos: Pos
    level: str

    def __le__(self, other):
        if self.line == "":
            return True
        else:
            return other.level.startswith(self.level)


## ColTeX datatype

ColTeX = List[Union["Def", "Inline", "Call", "Comment", "Pointer"]]


@dataclass
class Pointer:
    line: Line
    path: List[str]

    def up(self):
        return Pointer(None, self.path[:-1])

    def __hash__(self):
        return hash(".".join(self.path))

    def prefixes(self):
        for i in range(0, len(self.path) + 1):
            yield Pointer(None, self.path[0 : len(self.path) - i])

    def __add__(self, other):
        if isinstance(other, Pointer):
            return Pointer(None, self.path + other.path)
        elif isinstance(other, Def):
            if other.name == "rawtex":
                return self
            else:
                return Pointer(None, self.path + [other.name])
        else:
            raise ValueError(f"Adding incompatible pointer {self} with {other}")

    def __str__(self):
        p = ".".join(self.path)
        return f"@{p}"


@dataclass
class Def:
    line: Line
    name: str
    params: Optional[List[str]]
    body: List[ColTeX]

    def __str__(self):
        if self.params is None:
            x = f"{self.name}:"
            b = "".join(str(x) for x in self.body)
            return f"\n{x}\n{indent(b)}\n"
        else:
            p = ",".join(self.params)
            x = f"{self.name}({p}):"
            b = "".join(str(x) for x in self.body)
            return f"\n{x}\n{indent(b)}\n"


def is_variable_assignment(x):
    return isinstance(x, Def) and x.params is None


def is_function_definition(x):
    return isinstance(x, Def) and x.params is not None


@dataclass
class Inline:
    line: Line
    text: str

    def __str__(self):
        return self.text


@dataclass
class Comment:
    line: Line
    text: str


@dataclass
class Call:
    line: Line
    name: str
    params: List[Def]  # avec un bloc spécial qui s'appelle #argument#
    body: List[ColTeX]

    def __str__(self):
        if len(self.params) == 0 and len(self.body) == 0:
            return f":{self.name}"
        elif len(self.body) == 0:
            p = ",".join(str(e) for e in self.params)
            return f":{self.name}({p})"
        elif len(self.params) == 0:
            x = f"\n{self.name}:"
            b = "".join(str(x) for x in self.body)
            return f"{x}\n{indent(b)}\n"
        else:
            p = ",".join(str(e) for e in self.params)
            x = f"\n{self.name}({p}):"
            b = "".join(str(x) for x in self.body)
            return f"{x}\n{indent(b)}\n"


def coltexMap(f, p: ColTeX) -> ColTeX:
    if isinstance(p, Call):
        return Call(p.line, p.name, f(p.params), f(p.body))
    elif isinstance(p, Def):
        return Def(p.line, p.name, p.params, f(p.body))
    else:
        return p


def normalize_body(p: List[ColTeX]) -> Dict[str, Def]:
    return {e.name: e.body for e in p if isinstance(e, Def) and e.params is None}


def merge_inlines(p: List[ColTeX]) -> List[ColTeX]:
    def merge_inlines_unsafe(l):
        ctn = "".join(e.text for e in l)
        if ctn == "":
            return []
        else:
            return [Inline(l[0].line, ctn)]

    def mmap(l):
        return [coltexMap(merge_inlines, e) for e in l]

    return [
        x
        for inlines, l in itertools.groupby(p, lambda x: isinstance(x, Inline))
        for x in (merge_inlines_unsafe(list(l)) if inlines else mmap(l))
    ]
