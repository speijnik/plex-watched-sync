# -*- coding: utf-8 -*-
import typing

from plexapi.exceptions import NotFound
from plexapi.library import MovieSection, ShowSection
from plexapi.video import Movie, Season, Show, Video

from .log import Logger


def sync_sections(
    src: typing.Union[MovieSection, ShowSection],
    dst: typing.Union[MovieSection, ShowSection],
    logger: Logger,
):
    target_video_guid_map = {}
    for video in dst.all():
        target_video_guid_map.update(
            {
                video.guid: video,
            }
        )

    for src_video in src.all():
        target_video = target_video_guid_map.get(src_video.guid, None)
        if target_video is None:
            logger.warn(
                f"Skipping video {src_video.title} which is not present on target..."
            )
            continue

        sync_item(src_video, target_video, logger)


def sync_item(
    src_item: typing.Union[Show, Movie],
    target_item: typing.Union[Show, Movie],
    logger: Logger,
):
    if isinstance(src_item, Show):
        # special-case show
        sync_show(src_item, target_item, logger)
        return

    return sync_video(src_item, target_item, logger)


def sync_video(
    src_video: Video, target_video: Video, logger: Logger, title: str = None
):
    if not title:
        title = target_video.title

    if src_video.isWatched and not target_video.isWatched:
        target_video.markWatched()
        logger.info(f"Marked {title} as watched.")
    elif not src_video.isWatched and target_video.isWatched:
        logger.info(f"Marked {title} as unwatched.")
    else:
        logger.info(f"Skipping in-sync {title}")


def sync_show(src_show: Show, target_show: Show, logger: Logger):
    logger.info(f"Starting synchronization of show {src_show.title}")

    for src_season in src_show.seasons():
        try:
            target_season = target_show.season(src_season.title)
        except NotFound:
            logger.info(
                f"Skipping {src_show.title} {src_season.title}: not present on target"
            )
            continue

        sync_show_season(src_show, src_season, target_season, logger)


def sync_show_season(
    src_show: Show, src_season: Season, target_season: Season, logger: Logger
):
    logger.info(f"Starting synchronization of {src_show.title} {src_season.title}...")

    target_episode_map = {}
    for src_ep in target_season.episodes():
        target_episode_map.update(
            {
                src_ep.guid: src_ep,
            }
        )

    for src_ep in src_season.episodes():
        target_ep = target_episode_map.get(src_ep.guid, None)
        if not target_ep:
            logger.info(
                f"Skpping {src_show.title} {src_ep.seasonEpisode}: not present on target"
            )
            continue

        sync_video(
            src_ep, target_ep, logger, f"{src_show.title} {src_ep.seasonEpisode}"
        )
