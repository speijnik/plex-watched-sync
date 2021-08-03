# plex-watched-sync

*plex-watched-sync* is a small tool which helps you synchronize
the watched status of items on one Plex server to another Plex server.

The target is to provide a tool which can be used to synchronize watched
status information when copying contents to a new Plex instance.

## Usage

```bash
pip3 install plex-watched-sync
plex-watched-sync
```

**or** with [pipx](https://github.com/pypa/pipx#install-pipx):

```bash
pipx run plex-watched-sync
```

**or**

```bash
git clone https://github.com/speijnik/plex-watched-sync.git
cd plex-watched-sync
poetry install
poetry run plex-watched-sync
```
