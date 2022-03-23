#!/usr/bin/env python3
#
# LOPEZ Aliaume
#
# On an idea of Thomas Colcombet

# from dataclasses import dataclass
# from typing import List, Union, Dict, Optional
import itertools

from knowledge_pp.coltypes import *
from knowledge_pp.evaluator import *
from knowledge_pp.parsutils import *
from knowledge_pp.parser import *
from knowledge_pp.latex import *


def withLabel(env, params, position, body):
    _, params = reduce_forest(env, position, params)
    assert isinstance(params, list) and len(params) == 1
    assert isinstance(params[0], Def)
    assert len(params[0].body) == 1
    assert isinstance(params[0].body[0], Inline)
    label = params[0].body[0].text
    return [Def(None, label, None, body)]


def currentPosition(env, params, position, body):
    p = position.up().path
    if p == []:
        return [Inline(None, "")]
    else:
        return [Inline(None, ".".join(position.up().path) + ".")]


def evaluate_program(path):
    t, _ = coltex(list(iterate_file(path)))
    _, f = reduce_forest(
        {"withLabel": withLabel, "curpath": currentPosition}, Pointer(None, []), t
    )
    r = extract_pointers_forest(f)
    p = resolve_forest(r, Pointer(None, []), f)
    print(to_latex_list(p))
