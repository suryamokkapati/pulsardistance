#!/usr/bin/env python3
"""
pulsardistance - Pulsar distance estimation via full YMW16 and NE2001 models.
Uses pygedm (Price, Flynn & Deller 2021) which wraps the authoritative
C++/FORTRAN implementations of:
  - YMW16: Yao, Manchester & Wang (2017), ApJ, 835, 29
  - NE2001: Cordes & Lazio (2002, 2003), arXiv:astro-ph/0207156
"""

import sys
import math

# ---------------------------------------------------------------------------
# Dependency check — give a clear message if pygedm isn't installed
# ---------------------------------------------------------------------------
try:
    import pygedm
except ImportError:
    print("\n  [ERROR] pygedm is not installed.")
    print("  Install it with:  pip install pygedm --break-system-packages")
    print("  or:               pipx inject pulsardistance pygedm\n")
    sys.exit(1)

try:
    import astropy.units as u
    import astropy.coordinates as coord
except ImportError:
    print("\n  [ERROR] astropy is not installed.")
    print("  Install it with:  pip install astropy --break-system-packages\n")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Coordinate parsing
# ---------------------------------------------------------------------------

def parse_ra(ra_str):
    """Parse RA as HH:MM:SS.ss or decimal degrees → decimal degrees."""
    ra_str = ra_str.strip()
    if ':' in ra_str:
        parts = ra_str.split(':')
        h = float(parts[0])
        m = float(parts[1]) if len(parts) > 1 else 0.0
        s = float(parts[2]) if len(parts) > 2 else 0.0
        if not (0 <= h < 24):
            raise ValueError(f"RA hours out of range: {h}")
        return (h + m / 60.0 + s / 3600.0) * 15.0
    val = float(ra_str)
    if not (0.0 <= val < 360.0):
        raise ValueError(f"RA degrees out of range: {val}")
    return val


def parse_dec(dec_str):
    """Parse DEC as ±DD:MM:SS.ss or decimal degrees → decimal degrees."""
    dec_str = dec_str.strip()
    negative = dec_str.startswith('-')
    dec_str = dec_str.lstrip('+-')
    if ':' in dec_str:
        parts = dec_str.split(':')
        d = float(parts[0])
        m = float(parts[1]) if len(parts) > 1 else 0.0
        s = float(parts[2]) if len(parts) > 2 else 0.0
        val = d + m / 60.0 + s / 3600.0
    else:
        val = float(dec_str)
    val = -val if negative else val
    if not (-90.0 <= val <= 90.0):
        raise ValueError(f"DEC out of range: {val}")
    return val


def equatorial_to_galactic(ra_deg, dec_deg):
    """
    Convert J2000 equatorial (RA, Dec) to Galactic (l, b) using astropy,
    which applies the full IAU 1958 transformation.
    """
    sky = coord.SkyCoord(ra=ra_deg * u.degree, dec=dec_deg * u.degree,
                         frame='icrs')
    gal = sky.galactic
    return gal.l.deg, gal.b.deg


# ---------------------------------------------------------------------------
# Distance estimation via pygedm
# ---------------------------------------------------------------------------

def get_distances(dm_pc_cm3, l_deg, b_deg):
    """
    Run dm_to_dist for both YMW16 and NE2001 via pygedm.
    Returns dict with keys 'ymw16' and 'ne2001', each a dict with:
        dist_kpc  : float, distance in kpc
        tau_sc_ms : float, scattering time in ms at 1 GHz (or None)
    """
    results = {}

    for method in ('ymw16', 'ne2001'):
        try:
            dist, tau_sc = pygedm.dm_to_dist(l_deg, b_deg, dm_pc_cm3,
                                             method=method)
            # dist is an astropy Quantity in pc
            dist_kpc = dist.to(u.kpc).value
            # tau_sc is in seconds — convert to ms
            try:
                tau_ms = tau_sc.to(u.ms).value
            except Exception:
                tau_ms = None
            results[method] = {'dist_kpc': dist_kpc, 'tau_sc_ms': tau_ms}
        except Exception as e:
            results[method] = {'dist_kpc': None, 'tau_sc_ms': None,
                               'error': str(e)}

    return results


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_dist(d_kpc):
    """Return distance as a human-readable string."""
    if d_kpc is None:
        return "N/A"
    if d_kpc < 1.0:
        return f"{d_kpc * 1000.0:.1f} pc  ({d_kpc:.4f} kpc)"
    ly = d_kpc * 3261.56
    if ly >= 1000:
        return f"{d_kpc:.3f} kpc  ({ly / 1000:.2f} kly)"
    return f"{d_kpc:.3f} kpc  ({ly:.0f} ly)"


def fmt_tau(tau_ms):
    """Return scattering time as a human-readable string."""
    if tau_ms is None:
        return "N/A"
    if tau_ms < 1e-3:
        return f"{tau_ms * 1e6:.2f} ns"
    if tau_ms < 1.0:
        return f"{tau_ms * 1e3:.2f} µs"
    if tau_ms < 1000.0:
        return f"{tau_ms:.3f} ms"
    return f"{tau_ms / 1000:.3f} s"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║          PULSAR DISTANCE UTILITY         ║")
    print("  ╚══════════════════════════════════════════╝")
    print()

    try:
        ra_input  = input("  RA  : ").strip()
        dec_input = input("  DEC : ").strip()
        dm_input  = input("  DM  (pc cm⁻³) : ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\n  Aborted.")
        sys.exit(0)

    # --- Parse inputs -------------------------------------------------------
    try:
        ra_deg  = parse_ra(ra_input)
        dec_deg = parse_dec(dec_input)
    except ValueError as e:
        print(f"\n  [ERROR] Coordinate parse error: {e}")
        sys.exit(1)

    try:
        dm = float(dm_input)
        if dm <= 0:
            raise ValueError("DM must be positive.")
    except ValueError as e:
        print(f"\n  [ERROR] DM parse error: {e}")
        sys.exit(1)

    # --- Coordinate conversion ----------------------------------------------
    try:
        l_deg, b_deg = equatorial_to_galactic(ra_deg, dec_deg)
    except Exception as e:
        print(f"\n  [ERROR] Coordinate conversion failed: {e}")
        sys.exit(1)

    # --- Run models ---------------------------------------------------------
    print()
    print("  Computing distances via YMW16 and NE2001 …")
    results = get_distances(dm, l_deg, b_deg)

    # --- Output -------------------------------------------------------------
    ymw = results.get('ymw16', {})
    ne  = results.get('ne2001', {})

    print()
    print("  ═══════════════════════════════════════════════════════")
    print(f"  Equatorial (J2000)  RA  = {ra_deg:.6f}°   Dec = {dec_deg:.6f}°")
    print(f"  Galactic            l   = {l_deg:.4f}°     b   = {b_deg:.4f}°")
    print(f"  Dispersion Measure  DM  = {dm} pc cm⁻³")
    print("  ───────────────────────────────────────────────────────")
    print()

    if ymw.get('dist_kpc') is not None:
        print(f"  YMW16  (Yao, Manchester & Wang 2017)")
        print(f"    Distance         :  {fmt_dist(ymw['dist_kpc'])}")
        print(f"    Scattering time  :  {fmt_tau(ymw['tau_sc_ms'])}  (at 1 GHz)")
    else:
        print(f"  YMW16  : failed — {ymw.get('error', 'unknown error')}")

    print()

    if ne.get('dist_kpc') is not None:
        print(f"  NE2001 (Cordes & Lazio 2002)")
        print(f"    Distance         :  {fmt_dist(ne['dist_kpc'])}")
        print(f"    Scattering time  :  {fmt_tau(ne['tau_sc_ms'])}  (at 1 GHz)")
    else:
        print(f"  NE2001 : failed — {ne.get('error', 'unknown error')}")

    # Consensus note
    if ymw.get('dist_kpc') and ne.get('dist_kpc'):
        avg = (ymw['dist_kpc'] + ne['dist_kpc']) / 2.0
        diff_pct = abs(ymw['dist_kpc'] - ne['dist_kpc']) / avg * 100.0
        print()
        print(f"  Model mean         :  {fmt_dist(avg)}")
        print(f"  Model spread       :  {diff_pct:.1f}%")

    print()
    print("  ═══════════════════════════════════════════════════════")
    print()
    print("  References:")
    print("    YMW16  — Yao, Manchester & Wang (2017), ApJ 835, 29")
    print("    NE2001 — Cordes & Lazio (2002), arXiv:astro-ph/0207156")
    print("    PyGEDM — Price, Flynn & Deller (2021), PASA 38")
    print()


if __name__ == "__main__":
    main()
