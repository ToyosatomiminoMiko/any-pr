# Galactic Mission Control

A tiny epic: turn a contribution playground into a reproducible galaxy explorer.
Python 3.9+; standard library only; no network, dependencies, or file writes.

## Launch

From the repository root:

```sh
python -B galactic/mission.py --seed epic --stars 48 --jump 35
python -B galactic/mission.py --seed epic --jump 150 --json
python -B -m unittest discover -s galactic -p 'test_*.py' -v
```

`*` marks a star; `@` marks stars on the chosen route. Chart cells may overlap;
the JSON report retains every star's precise coordinates.

## Mission parameters

- `--seed`: reproducible string seed (default `any-pr`).
- `--stars`: 2–200 unique stars (default 24).
- `--origin`: starting star ID (default `S000`).
- `--destination`: target ID (default the last generated star).
- `--jump`: finite positive maximum distance per leg (default 30).
- `--json`: emit the full galaxy, route, and SHA-256 report fingerprint.

Dijkstra's algorithm minimizes total Euclidean travel distance, not hop count.
Jump limits include their boundary. Disconnected galaxies are expected: increase
jump range or select a closer destination. Exit status is 0 for a reachable
mission, 2 for an unreachable mission or invalid arguments.

The fingerprint identifies canonical report contents; it is not a signature or
proof of authenticity. Reproducibility is intended within the same Python
runtime: random implementation changes across Python versions may change maps.
Displayed route distance is rounded to three decimals after route selection.
The scanner is bounded to 200 stars and uses O(n²) neighbor comparisons.

This contribution does not modify the repository's governance, workflows,
license, README, or other contributors' work. Run only code you have reviewed.
