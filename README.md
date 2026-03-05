# pulsardistance

A command-line tool that estimates pulsar distances from dispersion measure using the YMW16 electron-density model

You can use the browser calculator from the PSC, but I prefer to stay in the terminal :)



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

### Arch 

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

---


## License

MIT
