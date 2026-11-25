# Ubuntu Package Tools

I made this after GDebi kept closing on my Ubuntu desktop. It lets me open a `.deb` in GDebi and install it through APT, or right-click an AppImage and add it to my app menu.

## Set it up

I tested this on Ubuntu 26.04 with GNOME Files on Wayland.

```sh
sudo apt update
sudo apt install git gdebi ptyxis python3-gi python3-nautilus zenity libfuse2t64 desktop-file-utils
git clone https://github.com/ayushxaw/ubuntu-package-tools.git
cd ubuntu-package-tools
./setup install
nautilus -q
```

Open Files again after the last command.

## Use it

- **DEB** — Right-click the file and choose **Open With → GDebi (APT in Terminal)**. Review the package in GDebi, then click **Install Package**. The terminal handles the password and shows APT's output. You can make this your default from **Open With**.
- **AppImage** — Right-click the file and choose **Install AppImage**. Look for it in your app menu. The copy lives in `~/Applications`, so you can clean up the original download afterward.

Have a direct download link? Paste it into this command, then open the file from Downloads.

```sh
~/.local/bin/ubuntu-package-download 'https://example.com/releases/example.AppImage'
```

The link needs HTTPS. If it ends in something like `/download`, add `--name example.AppImage`. Use `--directory` to save somewhere else.

## Remove it

Run `./setup uninstall` and restart Files with `nautilus -q`. Your installed apps stay in place. An AppImage added by this tool has a folder in `~/Applications` and a matching shortcut in `~/.local/share/applications`.

## Test it

```sh
/usr/bin/python3 -m unittest discover -s tests -v
```
