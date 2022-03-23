#!/usr/bin/env python3
#
# LOPEZ Aliaume
#
# On an idea of Thomas Colcombet
#
#
# FEATURES
#
# - Call by name
# - Dynamic scoping
# - Strict evaluation
# - No side effect
# - Strongly normalising

from knowledge_pp.coltypes import *


def reduce_node(env, c, program: ColTeX):

    if is_variable_assignment(program):
        return {**env, program.name: program}, [
            Def(
                program.line,
                program.name,
                None,
                reduce_forest(env, c + program, program.body)[1],
            )
        ]
    elif isinstance(program, Pointer):
        return env, [program]
    elif is_function_definition(program):
        return {**env, program.name: program}, [program]
    elif isinstance(program, Inline):
        return (env, [program])
    elif isinstance(program, Comment):
        return env, [Inline(program.line, "")]
    elif isinstance(program, Call):
        func = env.get(program.name, None)
        if func is None:
            _, body = reduce_forest(env, c, program.body)
            _, params = reduce_forest(env, c, program.params)
            return env, [Call(program.line, program.name, params, body)]
        elif callable(func):
            return (
                env,
                reduce_forest(
                    env,
                    c,
                    func(env=env, position=c, params=program.params, body=program.body),
                )[1],
            )
        elif isinstance(func, Def) and func.params is None:
            return reduce_forest(env, c, func.body)
        elif isinstance(func, Inline):
            return env, [func]
        else:
            # _, body = reduce_forest(env, c, program.body)
            # _, params = reduce_forest(env, c, program.params)
            body = program.body
            params = program.params

            nbody = normalize_body(body)
            nenv = {
                **env,
                **{
                    e: Def(
                        None,
                        "#argument#",
                        None,
                        nbody.get(
                            e,
                            [
                                Inline(
                                    program.line,
                                    f"Argument {i} to {program.name} not given",
                                )
                            ],
                        ),
                    )
                    if i >= len(params)
                    else params[i]
                    for i, e in enumerate(func.params)
                },
                "body": Def(None, "body", None, body),
            }
            return env, reduce_forest(nenv, c, func.body)[1]
    else:
        raise ValueError(f"invalid program {program} of type {type(program)}")


def reduce_forest(env, c, program: List[ColTeX]):
    accum = []
    for p in program:
        env, res = reduce_node(env, c, p)
        accum.extend(res)
    return env, merge_inlines(accum)


#####
#
# EVALUATE POINTERS
#
#####

References = Dict[Pointer, List[List[ColTeX]]]


def get_pointer(
    references: References, current: Pointer, pointer: Pointer
) -> List[ColTeX]:
    for pref in current.prefixes():
        r = references.get(pref + pointer, None)
        if r is not None and len(r) > 0:
            if len(r) == 1:
                return r[0]
            else:
                print("MULTIPLE POSSIBLE DEFINITIONS")
                return r[0]
    return [Inline(None, f"Undefined pointer {str(pointer)} in context {str(current)}")]


# WARNING, THIS USES IMPERATIVE MACHINERY !
def extract_pointers_node_i(r: References, c: Pointer, program):
    if isinstance(program, Def):
        l = r.setdefault(c + program, [])
        l.append(program.body)
        return extract_pointers_forest_i(r, c + program, program.body)


def extract_pointers_forest_i(r: References, c: Pointer, program):
    for p in program:
        extract_pointers_node_i(r, c, p)


# Functional wrapper
def extract_pointers_forest(program):
    r = {}
    extract_pointers_forest_i(r, Pointer(None, []), program)
    return r


#


def resolve_node(r, position, program):
    if isinstance(program, Pointer):
        return get_pointer(r, position, program)
    elif isinstance(program, Def):
        return [
            Def(
                program.line,
                program.name,
                program.params,
                resolve_forest(r, position + program, program.body),
            )
        ]
    elif isinstance(program, Call):
        return [
            Call(
                program.line,
                program.name,
                resolve_forest(r, position, program.params),
                program.body,
            )
        ]
    else:
        return [program]


def resolve_forest(r, position, program):
    return [e for p in program for e in resolve_node(r, position, p)]


example = [
    Def(
        None,
        "math",
        [],
        [
            Def(
                None,
                "rawtex",
                None,
                [
                    Inline(None, "\\begin{equation*}"),
                    Call(None, "body", [], []),
                    Call(None, "texttt", [], []),
                    Inline(None, "\\end{equation*}"),
                ],
            ),
            Inline(None, "here some math will be displayed"),
        ],
    ),
    Call(None, "math", [], [Inline(None, "Je suis un bout de maths")]),
]
