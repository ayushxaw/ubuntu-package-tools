from pathlib import Path
import subprocess

import gi

gi.require_version("Nautilus", "4.1")
from gi.repository import GLib, GObject, Nautilus


class AppImageInstaller(GObject.GObject, Nautilus.MenuProvider):
    def get_file_items(self, files):
        if len(files) != 1:
            return []

        file = files[0]
        if file.is_directory():
            return []
        path = file.get_location().get_path()
        if not path or Path(path).suffix.lower() != ".appimage":
            return []

        item = Nautilus.MenuItem(
            name="AppImageInstaller::install",
            label="Install AppImage",
            tip="Add this app to the Ubuntu app menu",
        )
        item.connect("activate", self.install, path)
        return [item]

    def install(self, item, path):
        installer = Path(GLib.get_user_data_dir()) / "ubuntu-package-installer" / "install-appimage"
        subprocess.Popen([str(installer), path])
