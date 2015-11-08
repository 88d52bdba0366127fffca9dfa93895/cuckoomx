# CuckooMX

This is a self-build Advanced Malware Detection for Mail based on Cuckoo
Sandbox

Have you ever heard an advanced persistent threat (APT) attack? If not, you
can read more about that [here](https://en.wikipedia.org/wiki/Advanced_persistent_threat)
There are many commercial products to protect you agains malware and APT, e.g
FireEye, Lastline, Cisco AMP,... But, is there any free products we can use?
Yes, it is Cuckoo Sandbox - a malware analysis system, and in here you can see
CuckooMX - an AMP for Mail based on Cuckoo Sandbox. CuckooMX will auto analyse
mails, including attachments and urls to detect malwares

## Installation

1. Install Cuckoo, instruction in [here](http://docs.cuckoosandbox.org/en/latest/)
2. Install CuckooMX

```bash
git clone https://github.com/88d52bdba0366127fffca9dfa93895/cuckoomx
```

3. In case you want to use extend web interface with CuckooMX, install via
command

```bash
/bin/bash ./cuckoomx/webmx/setup.sh
```

## Usage

Run CuckooMX via

```bash
python ./cuckoomx/cuckoomx.py
```

Run web interface via

```bash
python ./cuckoo/web/manage.py runserver 0.0.0.0:8000
```