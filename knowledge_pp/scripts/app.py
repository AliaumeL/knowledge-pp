import knowledge_pp.coltex as ct

import click


@click.command()
@click.argument(
    "template",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
def cli(template):
    """Template evaluation for LaTeX"""
    ct.evaluate_program(template)


if __name__ == "__main__":
    cli()
