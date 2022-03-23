#!/usr/bin/env python3
#
# LOPEZ Aliaume
#
# On an idea of Thomas Colcombet

from knowledge_pp.coltypes import Pointer, Def, Call, Inline, List, Line, ColTeX, merge_inlines

from knowledge_pp.parsutils import (
    is_space,
    is_token,
    is_symbol,
    takewhile1,
    take1,
    takewhile,
    fmap,
    above,
    lsymbol,
    repeat_until,
    sep_by,
    sep_by1,
    enclosed_by,
    does_not_start_with,
    take_char,
    spacify,
    chain,
    is_arg_symbol,
    choice,
    many,
    many1,
    listflatten,
)

## TINY PARSER COMBINATORS
## FIXME: performance issue
## TODO: error reporting with line numbers


spaces = takewhile1(is_space)
token = takewhile1(is_token)
symbols = takewhile1(is_symbol)


def elements(string):
    return fmap(lambda x: merge_inlines(listflatten(x)), many(element))(string)


def argument(string):
    return choice(
        fmap(
            lambda l: merge_inlines(
                listflatten([Inline(None, "("), l, Inline(None, ")")])
            ),
            enclosed_by(many(argument), "(", ")"),
        ),
        inline_elem,
        funcall,
        fmap(lambda s: [Inline(None, s)], takewhile1(is_arg_symbol)),
    )(string)


parameters = enclosed_by(sep_by(token, spacify(take_char(","))), "(", ")")
arguments = fmap(
    lambda args: merge_inlines(
        [Def(None, "#argument#", None, listflatten(arg)) for arg in args]
    ),
    sep_by(many1(does_not_start_with(")", argument)), take_char(",")),
)

pointer = fmap(
    lambda p: [Inline(None, p[0][:-1]), Pointer(None, p[1])],
    chain(lsymbol("@"), sep_by1(token, take_char("."))),
)

funcall = choice(
    fmap(
        lambda x: [Inline(None, x[0][:-1]), Call(None, x[1], x[4], [])],
        chain(
            lsymbol(":"),
            token,
            takewhile(is_space),
            take_char("("),
            arguments,
            take_char(")"),
        ),
    ),
    fmap(
        lambda x: [Inline(None, x[0][:-1]), Call(None, x[1], [], [])],
        chain(lsymbol(":"), token),
    ),
)

definition = choice(
    fmap(
        lambda x: [Def(None, x[0], x[1], [])], chain(token, parameters, take_char(":"))
    ),
    fmap(lambda x: [Def(None, x[0], None, [])], chain(token, take_char(":"))),
)

inline_elem = fmap(lambda x: [Inline(None, x)], token)
inline_symbols = fmap(lambda x: [Inline(None, x)], symbols)


def item_start(string):
    if len(string) > 1 and string[0] == "-" and is_space(string[1]):
        return [Call(None, "item", [], [])], string[1:]
    else:
        return None, string


element = choice(inline_elem, pointer, funcall, inline_symbols)


test = """
    Je suis un texte un peu complexe avec des :call:call
    et des :call(a,b)+:call(c)
    et puis des :call+:call
    et aussi des :call(a
    b, c, d
    e)

    Attention, il faut vérifier si
    :call((a+b)) est bien compris.

    On peut faire des choses plus complexes
    comme
    :BIGONE((:SMALL(x) + :LITTLE(y)), b)
"""


#### INDENTATION PARSER


def accumulate_lines(line):
    return repeat_until(lambda l: line <= l, blockline)


# extracts a bunch of lines
# corresponding to the same text block
def textlines(blocs):
    if len(blocs) == 0:
        return None, blocs

    pline = blocs[0]
    subcommands, rest = accumulate_lines(pline)(blocs[1:])
    if subcommands is None:
        subcommands = [pline]
    else:
        subcommands = [pline, *subcommands]

    fulltext = "\n".join(e.line for e in subcommands)

    result, _ = elements(fulltext)

    return result, rest


# extracts a block
def blockline(blocs):
    if len(blocs) == 0:
        return None, blocs

    pline = blocs[0]
    if pline.line == "":
        return None, blocs

    lvl = pline.level

    l, r = fmap(merge_inlines, choice(funcall, definition, item_start))(pline.line)

    if l is None or len(l) == 0:
        return None, blocs

    l = l[0]

    subcommands, rest = takewhile(above(lvl))(blocs[1:])

    if len(subcommands) == 0 and isinstance(l, Call) and l.name != "item":
        return None, blocs

    firstbody, _ = elements(r.lstrip())
    restbody, _ = coltex(subcommands)

    body = [*firstbody, *restbody]

    if isinstance(l, Call):
        l.body = body
        return [l], rest
    elif isinstance(l, Def):
        l.body = body
        return [l], rest
    else:
        return None, rest


coltex = fmap(listflatten, many(choice(blockline, textlines)))
