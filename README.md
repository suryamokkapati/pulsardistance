# pulsardistance 

A command-line utility for estimating pulsar distances from Right Ascension, Declination, and Dispersion Measure using a NE2001 model
The tool by the Pulsar Science Collaboratory works well, but I made this because I prefer to stay in the terminal :)

 





---

## Installation

Quick install

```bash
pip install .
```

Then just run from anywhere:

```bash
pulsardistance
```

Manual (no install)

```bash
python3 pulsardistance.py
```

---

Input formats

| Field | Accepted formats |
|-------|-----------------|
| RA    | `HH:MM:SS` or decimal degrees |
| DEC   | `DD:MM:SS` or decimal degrees (prefix `-` for south) |
| DM    | Positive float in pc cm⁻³ |

---

---

Uses Python 3.6+
