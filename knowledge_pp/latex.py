#!/usr/bin/env python3
#
# LOPEZ Aliaume
#
# On an idea of Thomas Colcombet

from knowledge_pp.coltypes import *


def to_latex(p: ColTeX) -> str:
    if is_variable_assignment(p):
        if p.name == "rawtex" or p.name == "#argument#":
            return to_latex_list([e for e in p.body if isinstance(e, (Def, Inline))])
        else:
            return to_latex_list([e for e in p.body if isinstance(e, Def)])

    elif isinstance(p, Inline):
        return p.text
    elif isinstance(p, Call) and len(p.body) == 0:
        return f"\\ukc{{{p.name}}}{{{to_latex_list(p.params)}}}"
    elif isinstance(p, Call) and len(p.body) > 0:
        q = to_latex_list(p.params)
        b = to_latex_list(p.body)
        return f"\\begin{{uke}}{{{p.name}}}{{{q}}}\n{indent(b)}\n\\end{{uke}}"
    elif isinstance(p, Pointer):
        return f"[{str(p)[1:]}]"
    else:
        return ""


def to_latex_list(p: List[ColTeX]) -> str:
    tmp = [to_latex(e) for e in p]
    return "".join(filter(lambda x: x != "", tmp))
