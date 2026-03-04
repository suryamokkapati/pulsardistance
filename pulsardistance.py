#!/usr/bin/env python3
"""
pulsardistance - A command-line utility for estimating pulsar distances
from RA, DEC, and Dispersion Measure (DM) using the NE2001 approximation.
"""

import sys
import math

NEUTRON_STAR = r"""
 --------------------------------------------------::@=--------------=-=---------------------------
 ------------------------------------------------:.-%-:--------------=-=---------------------------
 ---------------------------------=-------------:.%@-:---------------------------------------------
 ----------------------------------------------:-%+.:----------------------------------------------
 --------------------------------------------:.=@=:------------------------------------------------
 ------------------------+=-----------------..@%.:------------------------------------------------- 
 -----------------------:-+.---------------:.@..:--------------------------------------------------
 ------------------------*@.-------------:.%# .----------------------------------------------------
 -----------------------::= ------------::@=.------------------------------------------------------
 ------------------------:*+:----:-+--:.*#::-------------------------------------------------------
 ------------------------:#@.----.@:-:.%#.:--------------------------------------------------------
 -------------::---------:+#.---.%:..:*+=:---------------------------------------------------------
 ------------=%-.:-------:=*:--.-@ .=@@-:----------------------------------------------------------
 --------------*@* .:-----.*+...@  %*- :-------------------------------------------------------===- 
 --------------::-@@:  ---.@@ .@  @@.:--------:...------------------------------------------------- 
 ----------------:..-@%  ..-: = *@. .--:   :-+=@@+--------------------------------===-------------- 
 -------------------.  +@:..=-.@:   :-==@@@=-+:...--------------------------------===-------------- 
 -------::.               ...@.  @@@===:   :-------------------------------------------------------
 :      =+#@@@@@@@@@@@@@@@@@@@+=:     :--=========================================================*
 -@@@@@@@=:.         @@   .-. @+ .-@@@=-:   :--------------------------------------==-------------- 
 :      .:---=+@@@+-    :@- *: @@     :-=@@@==-...:---------------------==-------------------------
 -----------=-:   :--..+@ .-+-. @.@.:---:   :-=@@#*=-   :------------------------------------------
 -------------------::@ .::==:-:.%.##.:-------:   :-=@@@-=:   :------------------------------------
 ------------------:%*.:--:##:--:.=*:@+--::=:. .=*:::   :-+@@@+=-----------------------==----------
 ------------------@-:----:++:----:=@ :=-:@+ @*#@++*------:  .:------------------------------------
 -----------------:::-----:*+:-----:=@::-:-##. .=#=------------------------------------------------
 --------------------------#+:------:=%-:-:::---:::------------------------------------------------
 ------------------------:=*:--------:=*-:---------------------------------------------------------
 ------------------------:=*.---------::@=.--------------------------===---------------------------
 ------------------------:*@.----------:=@- -------------------------------------------------------
 ------------------------:#%.-----------.-@+ :-----------------------------------------------------
 ---------------------------:------------..@# :----------------------------------------------------
 -----------------------------------------: @@ .---------------------------------------------------
 ------------------------------------------: *@ .--------------------------------------------------
 -------------------------------------------: %@:.------------------------------------------------- 
 --------------------------------------------: -@%------------------------------------------------- 
"""

def parse_ra(ra_str):
    """Parse RA in HH:MM:SS or decimal degrees."""
    ra_str = ra_str.strip()
    if ':' in ra_str:
        parts = ra_str.split(':')
        h, m, s = float(parts[0]), float(parts[1]), float(parts[2]) if len(parts) > 2 else 0.0
        return (h + m / 60.0 + s / 3600.0) * 15.0  # convert hours to degrees
    return float(ra_str)

def parse_dec(dec_str):
    """Parse DEC in DD:MM:SS or decimal degrees."""
    dec_str = dec_str.strip()
    sign = -1 if dec_str.startswith('-') else 1
    dec_str = dec_str.lstrip('+-')
    if ':' in dec_str:
        parts = dec_str.split(':')
        d, m, s = float(parts[0]), float(parts[1]), float(parts[2]) if len(parts) > 2 else 0.0
        return sign * (d + m / 60.0 + s / 3600.0)
    return sign * float(dec_str)

def ra_dec_to_galactic(ra_deg, dec_deg):
    """
    Convert equatorial (RA, Dec) J2000 to galactic (l, b) coordinates.
    Uses the standard IAU transformation.
    """
    ra_rad  = math.radians(ra_deg)
    dec_rad = math.radians(dec_deg)

    # Galactic north pole in J2000: RA=192.85948°, Dec=27.12825°
    # Ascending node of galactic plane on equator: 32.93192°
    ra_ngp  = math.radians(192.85948)
    dec_ngp = math.radians(27.12825)
    l_asc   = math.radians(32.93192)   # l_NCP - 90°  → 122.93192 - 90

    sin_b = (math.sin(dec_ngp) * math.sin(dec_rad) +
             math.cos(dec_ngp) * math.cos(dec_rad) * math.cos(ra_rad - ra_ngp))
    b_rad = math.asin(sin_b)

    cos_b = math.cos(b_rad)
    sin_l = (math.cos(dec_rad) * math.sin(ra_rad - ra_ngp)) / cos_b
    cos_l = ((math.cos(dec_ngp) * math.sin(dec_rad) -
               math.sin(dec_ngp) * math.cos(dec_rad) * math.cos(ra_rad - ra_ngp)) / cos_b)

    l_rad = math.atan2(sin_l, cos_l) + l_asc
    l_deg = math.degrees(l_rad) % 360.0
    b_deg = math.degrees(b_rad)
    return l_deg, b_deg

def estimate_distance_ne2001(dm, l_deg, b_deg):
    """
    Estimate pulsar distance (kpc) from DM using a simplified NE2001-style
    model of the Galactic free-electron density.

    The model uses:
      - Thin disk  : n0=0.03 cm⁻³, scale height h1=0.14 kpc,  scale length A1=17.5 kpc
      - Thick disk : n0=0.01 cm⁻³, scale height h2=0.90 kpc,  scale length A2=17.5 kpc
      - Galactic centre: not included (negligible for most LOS)

    We integrate along the line of sight numerically and walk until the
    cumulative DM matches the requested DM, returning the path length.
    """
    l = math.radians(l_deg)
    b = math.radians(b_deg)

    cos_b = math.cos(b)
    sin_b = math.sin(b)
    cos_l = math.cos(l)
    sin_l = math.sin(l)

    # Sun's position in Galaxy
    R_sun = 8.5   # kpc

    # NE2001 thin + thick disk parameters
    n1, h1, A1 = 0.03,  0.14, 17.5
    n2, h2, A2 = 0.01,  0.90, 17.5

    def ne(d):
        """Free electron density at distance d (kpc) along the LOS."""
        x = R_sun - d * cos_b * cos_l
        y =         d * cos_b * sin_l
        z =         d * sin_b
        R = math.sqrt(x**2 + y**2)
        abs_z = abs(z)

        # Thin disk
        if A1 > 0:
            ne1 = n1 * math.exp(-abs_z / h1) * math.exp(-(R - R_sun) / A1) if R < R_sun + A1 else 0.0
        else:
            ne1 = 0.0

        # Thick disk
        ne2 = n2 * math.exp(-abs_z / h2) * math.exp(-(R - R_sun) / A2) if R < R_sun + A2 else 0.0

        return ne1 + ne2

    # Numerical integration: step 0.01 kpc, max 30 kpc
    step   = 0.01   # kpc
    dm_acc = 0.0
    d      = 0.0
    max_d  = 30.0   # kpc

    # Convert DM from pc cm⁻³ to kpc cm⁻³ factor: 1 kpc = 1000 pc
    dm_kpc = dm / 1000.0   # now in kpc·cm⁻³ (matching ne in cm⁻³ × kpc)

    while d < max_d:
        dm_acc += ne(d) * step
        d += step
        if dm_acc >= dm_kpc:
            break

    return d   # kpc

def format_distance(d_kpc):
    """Return a nicely formatted distance string."""
    if d_kpc < 1.0:
        return f"{d_kpc * 1000:.1f} pc  ({d_kpc:.4f} kpc)"
    return f"{d_kpc:.3f} kpc  ({d_kpc * 3261.56:.0f} light-years)"

def main():
    print(NEUTRON_STAR)
    print("  ╔══════════════════════════════════════════╗")
    print("  ║         PULSAR DISTANCE ESTIMATOR        ║")
    print("  ║     NE2001-based free-electron model     ║")
    print("  ╚══════════════════════════════════════════╝")
    print()
    print("  Enter pulsar coordinates and dispersion measure.")
    print("  RA  accepts HH:MM:SS  or decimal degrees.")
    print("  DEC accepts DD:MM:SS  or decimal degrees.")
    print()

    try:
        ra_input  = input("  RA  : ").strip()
        dec_input = input("  DEC : ").strip()
        dm_input  = input("  DM  (cm⁻³ pc) : ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\n  Aborted.")
        sys.exit(0)

    try:
        ra_deg  = parse_ra(ra_input)
        dec_deg = parse_dec(dec_input)
        dm      = float(dm_input)
    except (ValueError, IndexError):
        print("\n  [ERROR] Could not parse one or more inputs. Please check your values.")
        sys.exit(1)

    if dm <= 0:
        print("\n  [ERROR] DM must be a positive value.")
        sys.exit(1)

    l_deg, b_deg = ra_dec_to_galactic(ra_deg, dec_deg)
    distance_kpc = estimate_distance_ne2001(dm, l_deg, b_deg)

    print()
    print("  ─────────────────────────────────────────────")
    print(f"  Galactic coords  →  l = {l_deg:.4f}°   b = {b_deg:.4f}°")
    print(f"  DM               →  {dm} pc cm⁻³")
    print(f"  Est. distance    →  {format_distance(distance_kpc)}")
    print("  ─────────────────────────────────────────────")
    print()
    print("  Note: Based on a simplified NE2001 thin+thick disk model.")
    print("  For publication-quality distances use the full NE2001 or YMW16 model.")
    print()

if __name__ == "__main__":
    main()
