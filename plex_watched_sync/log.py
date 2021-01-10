# -*- coding: utf-8 -*-
import typing

import click
import typing_extensions


class Logger(typing_extensions.Protocol):
    """Logger protocol definition"""

    def log(self, msg):
        pass

    def info(self, msg):
        pass

    def warn(self, msg):
        pass

    def error(self, msg):
        pass


class ClickLogger(object):
    """Logger implementation based on click framework"""

    def log(self, msg):
        click.echo(msg)

    info = log

    def warn(self, msg: str):
        return self.log(click.style(msg, fg="yellow"))

    def error(self, msg: str):
        return self.log(click.style(msg, fg="red"))
