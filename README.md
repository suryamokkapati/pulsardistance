# pulsardistance 🌌

A simple command-line utility for estimating pulsar distances from **RA**, **DEC**, and **Dispersion Measure (DM)** using a simplified NE2001 free-electron density model.

```
$ pulsardistance

 [neutron star ASCII art]

  ╔══════════════════════════════════════════╗
  ║         PULSAR DISTANCE ESTIMATOR        ║
  ║     NE2001-based free-electron model     ║
  ╚══════════════════════════════════════════╝

  RA  : 05:34:31.97
  DEC : +22:00:52.1
  DM  (cm⁻³ pc) : 56.77

  ─────────────────────────────────────────────
  Galactic coords  →  l = 184.5575°   b = -5.7839°
  DM               →  56.77 pc cm⁻³
  Est. distance    →  2.031 kpc  (6626 light-years)
  ─────────────────────────────────────────────
```

---

## Installation

### Quick install (recommended)

```bash
pip install .
```

Then just run from anywhere:

```bash
pulsardistance
```

### Manual (no install)

```bash
python3 pulsardistance.py
```

---

## Input formats

| Field | Accepted formats |
|-------|-----------------|
| RA    | `HH:MM:SS` or decimal degrees |
| DEC   | `DD:MM:SS` or decimal degrees (prefix `-` for south) |
| DM    | Positive float in pc cm⁻³ |

---

## How it works

1. Converts equatorial (RA, Dec) J2000 to Galactic coordinates (l, b) using the standard IAU transformation.
2. Integrates the free-electron density along the line of sight using a two-component (thin + thick disk) approximation of the **NE2001** model (Cordes & Lazio 2002).
3. Returns the path length at which the cumulative DM equals the input DM.

> **Note:** This is a simplified model intended for quick estimates. For publication-quality distances, use the full [NE2001](https://www.nrl.navy.mil/rsd/RSDWWW/lazio/ne_model/) or [YMW16](http://www.atnf.csiro.au/research/pulsar/ymw16/) models.

---

## Requirements

- Python 3.6+
- No external dependencies (uses only the standard library)

---

## License

MIT
