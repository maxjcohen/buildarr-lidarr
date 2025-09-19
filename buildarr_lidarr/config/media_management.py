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
Lidarr plugin media management settings configuration.
"""

from __future__ import annotations

from logging import getLogger
from typing import Any, ClassVar, Dict, List, Optional, Set, cast

from buildarr.config import RemoteMapEntry
from buildarr.types import BaseEnum, NonEmptyStr
from pydantic import Field, NonNegativeInt
from typing_extensions import Annotated, Self

from ..api import api_delete, api_get, api_post, api_put
from ..secrets import LidarrSecrets
from .types import LidarrConfigBase

logger = getLogger(__name__)


class PropersAndRepacks(BaseEnum):
    """
    Propers and repacks configuration enumeration.
    """

    prefer_and_upgrade = "preferAndUpgrade"
    do_not_upgrade_automatically = "doNotUpgrade"
    do_not_prefer = "doNotPrefer"


class RescanArtistFolderAfterRefresh(BaseEnum):
    """
    Enumeration for rescan artist folder after refresh.
    """

    always = "always"
    after_manual_refresh = "afterManual"
    never = "never"


class ChangeFileDate(BaseEnum):
    """
    Change file date settings enumeration.
    """

    none = "none"
    local_air_date = "localAirDate"
    utc_air_date = "utcAirDate"


class ChmodFolder(BaseEnum):
    """
    Read-write permissions for media folders.
    """

    drwxr_xr_x = "755"
    drwxrwxr_x = "775"
    drwxrwx___ = "770"
    drwxr_x___ = "750"
    drwxrwxrwx = "777"

    @classmethod
    def validate(cls, v: Any) -> ChmodFolder:
        """
        Ensure that octal and decimal integers are both read properly by Buildarr.
        """
        try:
            return cls(oct(v)[2:] if isinstance(v, int) else v)
        except ValueError:
            try:
                return cls[v.replace("-", "_")]
            except (TypeError, KeyError):
                raise ValueError(f"Invalid {cls.__name__} name or value: {v}") from None


class LidarrMediaManagementSettingsConfig(LidarrConfigBase):
    """
    Naming, file management and root folder configuration.

    ```yaml
    lidarr:
      settings:
        media_management:
          ...
    ```

    For more information on how to configure these options correctly,
    refer to these guides from
    [WikiArr](https://wiki.servarr.com/lidarr/settings#media-management)
    and [TRaSH-Guides](https://trash-guides.info/Lidarr/Lidarr-recommended-naming-scheme).
    """

    # Tracks Naming
    rename_tracks: bool = False
    """
    Rename imported files to the defined standard format.

    Lidarr will use the existing file name if renaming is disabled.
    """

    replace_illegal_characters: bool = True
    """
    Replace illegal characters within the file name.

    If set to `False`, Lidarr will remove them instead.
    """

    delete_empty_folders: bool = False
    """
    Delete empty series and season folders during disk scan and when
    episode files are deleted.
    """

    skip_free_space_check: bool = False
    """
    Skip the free space check for the series root folder.

    Only enable when Lidarr is unable to detect free space from your series root folder.
    """

    minimum_free_space: Annotated[int, Field(ge=100)] = 100  # MB
    """
    Prevent import if it would leave less than the specified
    amount of disk space (in megabytes) available.

    Minimum value is 100 MB.
    """

    use_hardlinks: bool = True
    """
    Use hard links when trying to copy files from torrents that are still being seeded.

    Occasionally, file locks may prevent renaming files that are being seeded.
    You may temporarily disable seeding and use Lidarr's rename function as a work around.
    """

    import_extra_files: bool = False
    """
    Import matching extra files (subtitles, `.nfo` file, etc) after importing an episode file.
    """

    propers_and_repacks: PropersAndRepacks = PropersAndRepacks.do_not_prefer
    """
    Whether or not to automatically upgrade to Propers/Repacks.

    Values:

    * `prefer-and-upgrade`
    * `do-not-upgrade-automatically`
    * `do-not-prefer`

    ```yaml
    lidarr:
      settings:
        media_management:
          propers_and_repacks: "do-not-prefer"
    ```

    Use 'Do not Prefer' to sort by preferred word score over propers/repacks.
    Use 'Prefer and Upgrade' for automatic upgrades to propers/repacks.
    """

    analyze_video_files: bool = True
    """
    Extract video information such as resolution, runtime and codec information
    from files.

    This requires Lidarr to read parts of the file, which may cause high disk
    or network activity during scans.
    """

    rescan_artist_folder_after_refresh: RescanArtistFolderAfterRefresh = (
        RescanArtistFolderAfterRefresh.always
    )
    """
    Rescan the artist folder after refreshing the series.

    Values:

    * `always`
    * `after_manual_refresh`
    * `never`

    ```yaml
    lidarr:
      settings:
        media_management:
          rescan_artist_folder_after_refresh: "always"
    ```

    NOTE: Lidarr will not automatically detect changes to files
    if this option is not set to `always`.
    """
    change_file_date: ChangeFileDate = ChangeFileDate.none
    """
    Change file date on import/rescan.

    Values:

    * `none`
    * `local-air-date`
    * `utc-air-date`

    ```yaml
    lidarr:
      settings:
        media_management:
          change_file_date: "none"
    ```
    """

    recycling_bin: Optional[str] = None
    """
    Episode files will go here when deleted instead of being permanently deleted.
    """

    recycling_bin_cleanup: NonNegativeInt = 7  # days
    """
    Files in the recycle bin older than the selected number of days
    will be cleaned up automatically.

    Set to 0 to disable automatic cleanup.
    """

    # Permissions
    set_permissions: bool = False
    """
    Set whether or not `chmod` should run when files are imported/renamed.

    If you're unsure what this and the `chmod`/`chown` series of attributes do,
    do not alter them.
    """

    chmod_folder: ChmodFolder = ChmodFolder.drwxr_xr_x
    """
    Permissions to set on media folders and files during import/rename.
    File permissions are set without execute bits.

    This only works if the user running Lidarr is the owner of the file.
    It's better to ensure the download client sets the permissions properly.

    Values:

    * `drwxr-xr-x`/`755`
    * `drwxrwxr-x`/`775`
    * `drwxrwx---`/`770`
    * `drwxr-x---`/`750`
    * `drwxrwxrwx`/`777`

    ```yaml
    lidarr:
      settings:
        media_management:
          chmod_folder: "drwxr-xr-x"
    ```
    """

    chown_group: Optional[str] = None
    """
    Group name or gid. Use gid for remote file systems.

    This only works if the user running Lidarr is the owner of the file.
    It's better to ensure the download client uses the same group as Lidarr.
    """

    root_folders: Set[NonEmptyStr] = set()
    """
    This allows you to create a root path for a place to either
    place new imported downloads, or to allow Lidarr to scan existing media.

    ```yaml
    lidarr:
      settings:
        media_management:
          root_folders:
            - "/path/to/rootfolder"
    ```
    """

    delete_unmanaged_root_folders: bool = False
    """
    Delete root folder definitions from Lidarr if they are not
    explicitly defined in Buildarr.

    Before enabling this option, ensure all the root folders
    you want Lidarr to scan are defined in Buildarr,
    as Lidarr might remove imported media from its database
    when root folder definitions are deleted.

    *New in version 0.1.2.*
    """

    _naming_remote_map: ClassVar[List[RemoteMapEntry]] = [
        # Episode Naming
        ("rename_tracks", "renameTracks", {}),
    ]
    _mediamanagement_remote_map: ClassVar[List[RemoteMapEntry]] = [
        # Folders
        ("delete_empty_folders", "deleteEmptyFolders", {}),
        # Importing
        ("skip_free_space_check", "skipFreeSpaceCheckWhenImporting", {}),
        ("minimum_free_space", "minimumFreeSpaceWhenImporting", {}),
        ("use_hardlinks", "copyUsingHardlinks", {}),
        ("import_extra_files", "importExtraFiles", {}),
        # File Management
        ("propers_and_repacks", "downloadPropersAndRepacks", {}),
        ("rescan_artist_folder_after_refresh", "rescanAfterRefresh", {}),
        ("change_file_date", "fileDate", {}),
        (
            "recycling_bin",
            "recycleBin",
            {"decoder": lambda v: v or None, "encoder": lambda v: v or ""},
        ),
        ("recycling_bin_cleanup", "recycleBinCleanupDays", {}),
        # Permissions
        ("set_permissions", "setPermissionsLinux", {}),
        ("chmod_folder", "chmodFolder", {}),
        (
            "chown_group",
            "chownGroup",
            {"decoder": lambda v: v or None, "encoder": lambda v: v or ""},
        ),
    ]

    @classmethod
    def from_remote(cls, secrets: LidarrSecrets) -> Self:
        return cls(
            # Episode Naming
            **cls.get_local_attrs(
                cls._naming_remote_map,
                api_get(secrets, "/api/v1/config/naming"),
            ),
            # All other sections except Root Folders
            **cls.get_local_attrs(
                cls._mediamanagement_remote_map,
                api_get(secrets, "/api/v1/config/mediamanagement"),
            ),
            # Root Folders
            root_folders=set(
                cast(NonEmptyStr, rf["path"]) for rf in api_get(secrets, "/api/v1/rootfolder")
            ),
        )

    def update_remote(
        self,
        tree: str,
        secrets: LidarrSecrets,
        remote: Self,
        check_unmanaged: bool = False,
    ) -> bool:
        return any(
            [
                # Episode Naming
                self._update_remote_naming(
                    tree=tree,
                    secrets=secrets,
                    remote=remote,
                    check_unmanaged=check_unmanaged,
                ),
                # All other sections except Root Folders
                self._update_remote_mediamanagement(
                    tree=tree,
                    secrets=secrets,
                    remote=remote,
                    check_unmanaged=check_unmanaged,
                ),
                # Root Folders
                self._update_remote_rootfolder(
                    tree=f"{tree}.root_folders",
                    secrets=secrets,
                    remote=remote,
                    check_unmanaged=check_unmanaged,
                ),
            ],
        )

    def _update_remote_naming(
        self,
        tree: str,
        secrets: LidarrSecrets,
        remote: Self,
        check_unmanaged: bool = False,
    ) -> bool:
        updated, remote_attrs = self.get_update_remote_attrs(
            tree=tree,
            remote=remote,
            remote_map=self._naming_remote_map,
            check_unmanaged=check_unmanaged,
            set_unchanged=True,
        )
        if updated:
            config_id = api_get(secrets, "/api/v1/config/naming")["id"]
            api_put(
                secrets,
                f"/api/v1/config/naming/{config_id}",
                {"id": config_id, **remote_attrs},
            )
            return True
        return False

    def _update_remote_mediamanagement(
        self,
        tree: str,
        secrets: LidarrSecrets,
        remote: Self,
        check_unmanaged: bool = False,
    ) -> bool:
        updated, remote_attrs = self.get_update_remote_attrs(
            tree,
            remote,
            self._mediamanagement_remote_map,
            check_unmanaged=check_unmanaged,
            set_unchanged=True,
        )
        if updated:
            config_id = api_get(secrets, "/api/v1/config/mediamanagement")["id"]
            api_put(
                secrets,
                f"/api/v1/config/mediamanagement/{config_id}",
                {"id": config_id, **remote_attrs},
            )
            return True
        return False

    def _update_remote_rootfolder(
        self,
        tree: str,
        secrets: LidarrSecrets,
        remote: Self,
        check_unmanaged: bool = False,
    ) -> bool:
        changed = False
        current_root_folders: Dict[str, int] = {
            rf["path"]: rf["id"] for rf in api_get(secrets, "/api/v1/rootfolder")
        }
        for i, root_folder in enumerate(self.root_folders):
            if root_folder in current_root_folders:
                logger.debug("%s[%i]: %s (exists)", tree, i, repr(str(root_folder)))
            else:
                logger.info("%s[%i]: %s -> (created)", tree, i, repr(str(root_folder)))
                api_post(
                    secrets,
                    "/api/v1/rootfolder",
                    {
                        "path": str(root_folder),
                        "name": str(root_folder),
                        "defaultQualityProfileId": 1,
                        "defaultMetadataProfileId": 1,
                    },
                )
                changed = True
        return changed

    def delete_remote(self, tree: str, secrets: LidarrSecrets, remote: Self) -> bool:
        return self._delete_remote_rootfolder(
            tree=f"{tree}.root_folders",
            secrets=secrets,
            remote=remote,
        )

    def _delete_remote_rootfolder(self, tree: str, secrets: LidarrSecrets, remote: Self) -> bool:
        changed = False
        current_root_folders: Dict[str, int] = {
            rf["path"]: rf["id"] for rf in api_get(secrets, "/api/v1/rootfolder")
        }
        expected_root_folders = set(self.root_folders)
        i = -1
        for root_folder, root_folder_id in current_root_folders.items():
            if root_folder not in expected_root_folders:
                if self.delete_unmanaged_root_folders:
                    logger.info("%s[%i]: %s -> (deleted)", tree, i, repr(str(root_folder)))
                    api_delete(secrets, f"/api/v1/rootfolder/{root_folder_id}")
                    changed = True
                else:
                    logger.info("%s[%i]: %s -> (unmanaged)", tree, i, repr(str(root_folder)))
                i -= 1
        return changed
