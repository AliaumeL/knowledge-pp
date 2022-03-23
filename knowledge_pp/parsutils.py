#!/usr/bin/env python3
#
# LOPEZ Aliaume
#
# On an idea of Thomas Colcombet
#
# Small parser combinators
# DRAMATICALLY INEFFICIENT
#
# TODO:
#   - error handling and reporting
#   - work using the Line datatype

from knowledge_pp.coltypes import *


special_symbols = " \t\n()[]{}:\\-+=/|<>-_;,#%$*@.\"'"
reserved_symbols = ",()"


def is_space(c):
    return c in " \t\n\r"


def is_token(c):
    return c not in special_symbols


def is_symbol(c):
    return c in special_symbols


def is_arg_symbol(c):
    return is_symbol(c) and c not in reserved_symbols


def listflatten(l):
    accum = []
    for e in l:
        if isinstance(e, list):
            accum.extend(listflatten(e))
        else:
            accum.append(e)
    return accum


######
# PARSING INDENTATIONS
######


def compute_indent(pline):
    line = pline["line"].rstrip()
    stripped = line.lstrip()
    size = len(line) - len(stripped)
    prefix = line[0:size]
    return Line(level=prefix, pos=pline["pos"] + size, line=stripped)


def iterate_file(path):
    """
    Iterates over the lines of a filepath
    and produces Lines object with correct
    source/positions
    """
    with open(path, "r") as f:
        for num, line in enumerate(f.readlines()):
            yield compute_indent({"pos": Pos(path, num, 0), "line": line})


def above(x):
    """
    Level comparison (strict)
    """
    return lambda y: y.line == "" or (y.level != x and y.level.startswith(x))


####
# PARSER COMBINATORS
####


def take1(p):
    def δ(l):
        if len(l) > 0 and p(l[0]):
            return l[0], l[1:]
        else:
            return None, l

    return δ


def takewhile(p):
    def δ(l):
        try:
            i = 0
            while i < len(l) and p(l[i]):
                i += 1
            return l[0:i], l[i:]
        except IndexError:
            print(f"error {l}")
            return [], []

    return δ


def takewhile1(p):
    return fmap(lambda x: None if x == "" else x, takewhile(p))


def lsymbol(c):
    return fmap(
        lambda x: x if len(x) > 0 and x[-1] == c else None, takewhile(is_symbol)
    )


def take_char(c):
    def δ(l):
        if len(l) > 0 and l[0] == c:
            return c, l[1:]
        else:
            return None, l

    return δ


def chain(*parsers):
    def δ(l):
        r = l
        accum = []
        for p in parsers:
            x, r = p(r)
            if x is None:
                return None, l
            accum.append(x)
        return accum, r

    return δ


def does_not_start_with(char, parser):
    def δ(l):
        if len(l) > 0 and l[0] == char:
            return None, l
        else:
            return parser(l)

    return δ


def fmap(f, parser):
    def δ(l):
        v, r = parser(l)
        if v is not None:
            return f(v), r
        else:
            return None, l

    return δ


def spacify(parser):
    p = chain(takewhile(is_space), parser, takewhile(is_space))
    return fmap(lambda x: x[1], p)


def enclosed_by(parser, a, b):
    p = chain(spacify(take_char(a)), parser, spacify(take_char(b)))
    return fmap(lambda x: x[1], p)


def sep_by(parser, separator):
    def δ(l):
        elems = []
        seenSep = True
        restP = l
        restS = l
        while seenSep is not None:
            v0, restPt = parser(restS)
            if v0 is None:
                break
            restP = restPt
            elems.append(v0)
            seenSep, restS = separator(restP)
        return elems, restP

    return δ


def repeat_until(condition, stopword):
    def δ(l):
        i = 0
        v0 = None
        while v0 is None and i < len(l) and condition(l[i]):
            v0, _ = stopword(l[i:])
            if v0 is None:
                i = i + 1
        if i <= 1:
            return None, l
        else:
            return l[:i], l[i:]

    return δ


def sep_by1(parser, separator):
    return fmap(lambda x: None if len(x) == 0 else x, sep_by(parser, separator))


def sep_by1_accum(parser, separator):
    def δ(l):
        old = l
        elems = []
        seenSep = True
        while seenSep is not None:
            v0, l = parser(l)
            if v0 is None:
                break
            elems.append(v0)
            seenSep, l = separator(l)
            if seenSep is not None:
                elems.append(seenSep)

        if len(elems) == 0:
            return None, old
        else:
            return elems, l

    return δ


def many(parser):
    def δ(l):
        elems = []
        while len(l) > 0:
            v0, lt = parser(l)
            if v0 is None:
                break
            l = lt
            elems.append(v0)
        return elems, l

    return δ


def many1(parser):
    return fmap(lambda x: None if len(x) == 0 else x, many(parser))


def choice(*parsers):
    def δ(l):
        for p in parsers:
            v, r = p(l)
            if v is not None:
                return v, r
        return None, l

    return δ
