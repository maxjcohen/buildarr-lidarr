# Copyright (C) 2023 Callum Dickinson
#
# Buildarr is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# Buildarr is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Buildarr.
# If not, see <https://www.gnu.org/licenses/>.


"""
Lidarr plugin interface.
"""

from __future__ import annotations

from buildarr.plugins import Plugin

from . import __version__
from .cli import lidarr
from .config import LidarrConfig
from .manager import LidarrManager
from .secrets import LidarrSecrets


class LidarrPlugin(Plugin):
    """
    Lidarr plugin class that Buildarr reads to process Lidarr instances.
    """

    cli = lidarr
    config = LidarrConfig
    manager = LidarrManager
    secrets = LidarrSecrets
    version = __version__
