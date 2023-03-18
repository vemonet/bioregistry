# -*- coding: utf-8 -*-

"""Web command for running the app."""

from pathlib import Path
from typing import Optional

import click
from more_click import (
    flask_debug_option,
    gunicorn_timeout_option,
    host_option,
    port_option,
    run_app,
    verbose_option,
    with_gunicorn_option,
    workers_option,
)

__all__ = [
    "web",
]


@click.command()
@host_option
@port_option
@with_gunicorn_option
@workers_option
@verbose_option
@gunicorn_timeout_option
@flask_debug_option
@click.option("--registry", type=Path, help="Path to a local registry file")
@click.option("--metaregistry", type=Path, help="Path to a local metaregistry file")
@click.option("--collections", type=Path, help="Path to a local collections file")
@click.option("--contexts", type=Path, help="Path to a local contexts file")
@click.option("--config", type=Path, help="Path to a configuration file")
@click.option(
    "--base-url",
    type=str,
    default="https://bioregistry.io",
    show_default=True,
    help="Base URL for app",
)
@click.option("--with-uvicorn", is_flag=True, type=bool, default=False, help="Deploy with uvicorn for development")
def web(
    host: str,
    port: str,
    with_gunicorn: bool,
    with_uvicorn: bool,
    workers: int,
    debug: bool,
    timeout: Optional[int],
    registry: Optional[Path],
    metaregistry: Optional[Path],
    collections: Optional[Path],
    contexts: Optional[Path],
    config: Optional[Path],
    base_url: Optional[str],
):
    """Run the web application."""
    from .impl import get_app
    from ..resource_manager import Manager

    manager = Manager(
        registry=registry,
        metaregistry=metaregistry,
        collections=collections,
        contexts=contexts,
        # is being able to load custom mismatches necessary?
        base_url=base_url,
    )
    app = get_app(
        manager=manager,
        config=config,
        first_party=registry is None
        and metaregistry is None
        and collections is None
        and contexts is None,
    )
    if with_uvicorn:
        # TODO: Hotfix to use uvicorn in development, might want to be improved
        import uvicorn
        log_level="info"
        if debug:
            log_level = "debug"
        uvicorn.run(app, port=port, log_level=log_level, host=host)
    else:
        run_app(
            app=app,
            host=host,
            port=port,
            workers=workers,
            with_gunicorn=with_gunicorn,
            debug=debug,
            timeout=timeout,
        )
