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
Lidarr plugin exception classes.
"""

from __future__ import annotations

from buildarr.exceptions import BuildarrError


class LidarrError(BuildarrError):
    """
    Lidarr plugin exception base class.
    """

    pass


class LidarrAPIError(LidarrError):
    """
    Lidarr API exception class.
    """

    def __init__(self, msg: str, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(msg)


class LidarrSecretsError(LidarrError):
    """
    Lidarr plugin secrets exception base class.
    """

    pass


class LidarrSecretsUnauthorizedError(LidarrSecretsError):
    """
    Error raised when Buildarr was unable to authenticate with Lidarr.
    """

    pass
