# 03 — Software installation

Everything here is local. Nothing connects to a server and nothing touches the
car yet.

## What you need

- Python 3.9 or newer (`python3 --version`)
- `git`
- On macOS: the command line developer tools, if `python3` is not present yet
  (`xcode-select --install`)

## Get the code

```bash
git clone https://github.com/cheapjourney/smart453-tomtom-research.git
cd smart453-tomtom-research
```

## Create an isolated environment

Do not install into the system Python. A virtual environment keeps the tools and
their one dependency away from everything else on the machine.

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r tools/requirements.txt
```

`tools/requirements.txt` contains exactly one runtime dependency: **pyserial**.
The tools use nothing else outside the standard library.

## Run the offline tests

The test suite needs no car and no adapter. It starts a mock head unit and talks
to it through a pseudo-terminal, so it exercises the same code path as a real
connection.

```bash
python -m unittest discover -s tests -v
```

Expected: **36 tests, all pass**. If `socat` is missing the write-tool tests fail
with a clear error; install it first:

```bash
brew install socat      # macOS
sudo apt install socat  # Debian/Ubuntu
```

If the decoder tests fail, stop — the installation is broken and nothing else
should be attempted.

## Local configuration

The write tool is locked twice. The first lock is a file that does not exist in
the repository:

```bash
cp config/aa_write.example.json config/aa_write.json
```

It stays at `"enabled": false` until you deliberately change it, and
`config/aa_write.json` is git-ignored so your local state is never committed.

Run logs go to `logs/`, also ignored.

## DDT4All (optional, separate)

Many guides use **DDT4All** instead of these tools. It is a Windows-oriented
Python/Qt application with its own vehicle database, licensed GPL-3.0 by its
authors. Nothing from it is included here — not the program, not the database, not
code. If you use it, install it from its own repository and follow its own
documentation; see `06-android-auto-activation.md` for what that route involves
and what this project has and has not verified about it.

## The Bluetooth bridge (macOS)

If your adapter's serial port works normally, you do not need this. On macOS 12
with an OBDLink MX+, the persisted `/dev/cu.*` device stopped working after the
first session in this project. The fix is a small RFCOMM-to-serial bridge, kept in
a separate repository:

<https://github.com/cheapjourney/obdlink-macos-rfcomm-bridge>

Nothing from that project is copied here; `04-obdlink-connection.md` explains how
the two fit together. A summary of what the bridge does — and the phone-blocks-the-
adapter trap — is in the README section *Companion project: OBDLink macOS Bluetooth
RFCOMM Bridge*.
