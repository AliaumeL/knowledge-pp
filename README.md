# knowledge-pp

[![PyPI](https://img.shields.io/pypi/v/knowledge-pp.svg)](https://pypi.python.org/pypi/knowledge-pp)

Preprocessor for the
[knowledge LaTeX package](https://ctan.org/pkg/knowledge).


## Status

This is a proof of concept, **do not use it**.
An example document can be found in `examples/` along
with a Makefile to generate a document called `main.pdf`.

## Wanted Features

1. LSP support via https://github.com/openlawlibrary/pygls
2. Strongly terminating
3. Lexical scoping by default
4. Contexts à la React (dynamic scoping)
5. Hooks for `custom DSL` languages, that are left un-interpreted
6. A math mode as a custom DSL

## How to use

Given a valid document, you can simply run

	kwpp my_document 

To get the corresponding LaTeX output.

In practise, this is intended to be used in a workflow using a Makefile,
or the specific input triggers from latexmk.


## Devel using virtualenv

Using virtualenv and the `--editable` option from `pip3` allows for an easy
setup of a development environment that will match a future user install without
the hassle.

For bash and Zsh users

```bash
virtualenv -p python3 kw-devel
source ./kw-devel/bin/activate
pip3 install --editable .
```

For fish users

```fish
virtualenv -p python3 kw-devel
source ./kw-devel/bin/activate.fish
pip3 install --editable .
```
