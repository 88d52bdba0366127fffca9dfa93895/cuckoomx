# CuckooMX

This is a self-build Advanced Malware Detection (AMD) for Mail based on Cuckoo
Sandbox

Have you ever heard an advanced persistent threat (APT) attack? If not, you
can read more about that [here]
(https://en.wikipedia.org/wiki/Advanced_persistent_threat).
There are many commercial products to protect you against malware and APT, e.g
FireEye, Lastline, Cisco AMP,... But, is there any free products we can use?
Yes, it is Cuckoo Sandbox - a malware analysis system, and in here you can see
CuckooMX - an AMD for Mail based on Cuckoo Sandbox. CuckooMX will auto analyse
mails, including attachments and URLs to detect malwares

## Installation

1. Install Cuckoo, instruction in [here]
(http://docs.cuckoosandbox.org/en/latest/)
2. Install CuckooMX

```bash
git clone https://github.com/88d52bdba0366127fffca9dfa93895/cuckoomx
```

3. In case you want to use extended web interface with CuckooMX, install it 
via command

```bash
/bin/bash ./cuckoomx/webmx/setup.sh
```

## Configuration

In CuckooMX, we have 2 modes inline and offside, but now inline mode is under
development.

To use offside mode, enabled this mode in config file and edit parameter 
`store` in `[offside]` section, it is where you store mails

```bash
[offside]
enalbed = yes
store = /opt/zimbra/store/
```

## Usage

Run Cuckoo via

```bash
python ./cuckoo/cuckoo.py
```

Run Cuckoo API via

```bash
python ./cuckoo/utils/api.py --host 127.0.0.1 --port 8090
```

Run CuckooMX via

```bash
python ./cuckoomx/cuckoomx.py
```
