# pulsardistance 

A command-line utility for estimating pulsar distances from **RA**, **DEC**, and **Dispersion Measure**. Uses electron density models via [PyGEDM](https://github.com/FRBs/pygedm) 

I got tired of keeping on having to load up the web page for the GBT calculator so I just made one for the command-line. I also just prefer to stay in the terminal :)

Both models are run on every query and displayed side by side, along with a pulse scattering time estimate and model spread percentage.

```
  ╔══════════════════════════════════════════╗
  ║          PULSAR DISTANCE UTILITY         ║
  ╚══════════════════════════════════════════╝

  RA  : 05:34:31.97
  DEC : +22:00:52.1
  DM  (pc cm⁻³) : 56.77

  Computing distances via YMW16 and NE2001 …

  ═══════════════════════════════════════════════════════
  Equatorial (J2000)  RA  = 83.633208°   Dec = 22.014472°
  Galactic            l   = 184.5575°     b   = -5.7839°
  Dispersion Measure  DM  = 56.77 pc cm⁻³
  ───────────────────────────────────────────────────────

  YMW16  (Yao, Manchester & Wang 2017)
    Distance         :  2.031 kpc  (6626 ly)
    Scattering time  :  0.084 ms  (at 1 GHz)

  NE2001 (Cordes & Lazio 2002)
    Distance         :  1.930 kpc  (6296 ly)
    Scattering time  :  0.061 ms  (at 1 GHz)

  Model mean         :  1.981 kpc  (6461 ly)
  Model spread       :  5.1%

  ═══════════════════════════════════════════════════════

  References:
    YMW16  — Yao, Manchester & Wang (2017), ApJ 835, 29
    NE2001 — Cordes & Lazio (2002), arXiv:astro-ph/0207156
    PyGEDM — Price, Flynn & Deller (2021), PASA 38
```

---

## Models

| Model | Paper | Description |
|-------|-------|-------------|
| **YMW16** | Yao, Manchester & Wang (2017), ApJ 835, 29 | Current state-of-the-art. Calibrated on 189 pulsars with independent distances. First model to support extragalactic pulsars and FRBs. |
| **NE2001** | Cordes & Lazio (2002, 2003), arXiv:astro-ph/0207156 | Long-established standard. Multi-component Galactic electron density model. |

Both are run via [PyGEDM](https://github.com/FRBs/pygedm) (Price, Flynn & Deller 2021, PASA 38), which wraps the original C++ and FORTRAN implementations directly.

---

## Installation

```bash
# Clone and enter the repo
git clone https://github.com/YOUR_USERNAME/pulsardistance.git
cd pulsardistance

# Install with pipx (recommended on Debian/Ubuntu)
pipx install .
```

Then run from anywhere:

```bash
pulsardistance
```

To update after pulling changes:

```bash
pipx install . --force
```

---

## Input formats

| Field | Accepted formats | Example |
|-------|-----------------|---------|
| RA    | `HH:MM:SS.ss` or decimal degrees | `05:34:31.97` or `83.633` |
| DEC   | `±DD:MM:SS.ss` or decimal degrees | `+22:00:52.1` or `22.014` |
| DM    | Positive float (pc cm⁻³) | `56.77` |

---

## Requirements

- Python ≥ 3.7
- [pygedm](https://github.com/FRBs/pygedm)
- [astropy](https://www.astropy.org/)

Both are installed automatically via `pipx install .`

---

## Accuracy

YMW16 estimates that 95% of predicted Galactic pulsar distances will have a relative error of less than a factor of 0.9. When the two models agree closely (small spread %), confidence in the estimate is higher. Large spread values indicate a line of sight where the models differ and additional caution is warranted.

---

## License

MIT
