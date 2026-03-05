# pulsar

A minimal command-line tool that estimates pulsar distances from dispersion measure using the **YMW16** electron-density model (Yao, Manchester & Wang 2017).

```
+--------------------------------------+
|       PULSAR DISTANCE UTILITY        |
+--------------------------------------+

Right Ascension (degrees, J2000): 83.8221
Declination     (degrees, J2000): 22.0144
Dispersion Measure (pc/cm^3):     56.791

Galactic longitude l = 184.5575 deg
Galactic latitude  b = -5.7843 deg

--- YMW16 Result ---
Distance : 2.038 kpc  (2038.0 pc)
```

---

## Installation

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install gcc make
git clone https://github.com/YOUR_USERNAME/pulsar.git
cd pulsar
make
sudo make install
```

### Arch Linux

```bash
sudo pacman -S gcc make
git clone https://github.com/YOUR_USERNAME/pulsar.git
cd pulsar
make
sudo make install
```

The binary is installed to `/usr/local/bin/pulsar`.

---

## Usage

```
pulsar
```

You will be prompted for:

| Input | Description | Example |
|---|---|---|
| Right Ascension | J2000 degrees | `83.8221` |
| Declination | J2000 degrees | `22.0144` |
| Dispersion Measure | pc cm⁻³ | `56.791` |

The tool converts RA/Dec to Galactic coordinates, then integrates the YMW16 free-electron model along the line of sight until the accumulated DM matches your input.

---

## Uninstall

```bash
sudo make uninstall
```

---

## Model reference

Yao, J. M., Manchester, R. N., & Wang, N. (2017).  
*A New Electron-density Model for Estimation of Pulsar and FRB Distances.*  
ApJ, 835, 29.  
https://doi.org/10.3847/1538-4357/835/1/29

---

## License

MIT
