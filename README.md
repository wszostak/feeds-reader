# Feeds Reader

## Quick start

First create and activate virtualenv.

```bash
python3 -m venv venv
. ./venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Finally, create file `feeds.txt` with one url per line. You can use `#` at the beginning to ignore the line. Then run:

```
python read.py
```
