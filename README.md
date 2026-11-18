# hyperion-dust

A library of dust models for the
[Hyperion](http://www.hyperion-rt.org) radiative transfer code.

The package contains the tabulated optical properties for each dust model,
and builds Hyperion dust objects and HDF5 dust files from them on request, so
the (much larger) HDF5 files do not need to be distributed.

## Installation

    pip install hyperion-dust

## Dust models

| Name | Description |
|---|---|
| `kmh94_3.1_hg` | Kim, Martin & Hendry (1994) with R_V=3.1, assuming Henyey-Greenstein scattering |
| `kmh94_3.1_full` | Kim, Martin & Hendry (1994) with R_V=3.1, with the full scattering matrix |
| `d03_3.1_6.0_A` | Draine (2003) Milky Way model with R_V=3.1 |
| `d03_4.0_4.0_A` | Draine (2003) Milky Way model "A" with R_V=4.0 |
| `d03_5.5_3.0_A` | Draine (2003) Milky Way model "A" with R_V=5.5 |

The opacities are per unit mass of dust. The Draine (2003) models were
computed with a wrapper around the bhmie code and do not reproduce the
published properties exactly since there is no special treatment of small
grains (see `hyperion_dust/data/d03/README.md`).

The names can be listed with:

```python
>>> from hyperion_dust import available_dust
>>> available_dust()
['d03_3.1_6.0_A', 'd03_4.0_4.0_A', 'd03_5.5_3.0_A', 'kmh94_3.1_full', 'kmh94_3.1_hg']
```

## Usage

To get a dust object that can be assigned to a density component of a
Hyperion model:

```python
from hyperion_dust import get_dust

dust = get_dust('d03_5.5_3.0_A')
```

To include dust sublimation, give the sublimation mode (`'fast'`, `'slow'`
or `'cap'`, as defined by `SphericalDust.set_sublimation_temperature` in
Hyperion) and the sublimation temperature in K:

```python
dust = get_dust('d03_5.5_3.0_A', sublimation_mode='fast',
                sublimation_temperature=1600)
```

To get the path to an HDF5 dust file instead, use `get_dust_filename`, which
takes the same arguments:

```python
from hyperion_dust import get_dust_filename

filename = get_dust_filename('d03_5.5_3.0_A', sublimation_mode='fast',
                             sublimation_temperature=1600)
```

The file is generated the first time it is requested, which takes about a
second, and is then re-used. Files are stored in the astropy cache directory
by default (pass `cache_dir=` to use a different location) and are kept
separately for each version of this package and of Hyperion.
