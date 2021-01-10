# -*- coding: utf-8 -*-
import sys
import typing

import click
from plexapi.exceptions import BadRequest
from plexapi.library import MovieSection, ShowSection
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer

from .log import ClickLogger
from .sync import sync_sections

logger = ClickLogger()


def _select_section(
    name: str, conn: PlexServer
) -> typing.Union[MovieSection, ShowSection]:
    all_sections = conn.library.sections()
    section_map = {}
    for section in all_sections:
        if not isinstance(section, MovieSection) and not isinstance(
            section, ShowSection
        ):
            continue

        section_name = f"{section.title} [{section.key}]"
        section_map.update(
            {
                section_name: section,
            }
        )

    section_names = list(sorted(section_map.keys()))

    section_name = click.prompt(
        f"Select {name} section", type=click.Choice(section_names)
    )

    return section_map[section_name]


@click.command()
@click.version_option()
def main():
    """plex-watched-sync synchronizes the watched state of items on one Plex
    server to another

    """

    plex_user = click.prompt("Please enter your Plex username", type=str)
    plex_pass = click.prompt(
        "Please enter your Plex password", type=str, hide_input=True
    )

    logger.info("Authenticating...")
    try:
        account = MyPlexAccount(plex_user, plex_pass)
    except BadRequest as e:
        logger.error(f"Authentication failed: {e}")
        sys.exit(1)

    logger.info(f"Successfully authenticated with Plex (account_id={account.id})")

    server_resources = list(
        filter(lambda resource: resource.provides == "server", account.resources())
    )

    if len(server_resources) < 2:
        logger.error("Aborting, less than 2 servers found...")
        sys.exit(2)

    server_resource_map = {}
    for resource in server_resources:
        server_resource_map.update(
            {
                resource.name: resource,
            }
        )

    server_names = list(sorted(server_resource_map.keys()))

    source_server_name = click.prompt(
        "Source server", type=click.Choice(server_names), show_choices=True
    )
    source_server = server_resource_map[source_server_name]
    del server_resource_map[source_server_name]

    # pick first server saving us a prompt if there are only two servers
    target_server_name = list(server_resource_map.keys())[0]

    if len(server_resource_map) > 1:
        target_server_name = click.prompt(
            "Target server",
            type=click.Choice(list(sorted(server_resource_map.keys()))),
            show_choices=True,
        )

    target_server = server_resource_map[target_server_name]

    logger.info(f"Connecting to source server {source_server.name}...")
    source_conn = source_server.connect()
    source_section = _select_section("source", source_conn)

    logger.info(f"Connecting to target server {target_server.name}...")
    target_conn = target_server.connect()
    target_section = _select_section("target", target_conn)

    logger.info("Summary: ")
    logger.info(f"Source server  : {source_server_name}")
    logger.info(f"Source section : {source_section.title}")
    logger.info(f"Target server  : {target_server_name}")
    logger.info(f"Target section : {target_section.title}")

    if source_section.type != target_section.type:
        logger.warn("Source and target section types do not match")

    click.confirm("Are you sure you want to start the synchronization processs?")
    sync_sections(source_section, target_section, logger)
