import os
import tempfile
from importlib.metadata import PackageNotFoundError, version

__all__ = ["available_dust", "get_dust", "get_dust_filename"]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# For each dust model, the format of the input tables and their location
# relative to the data directory. For the bhmie format the location is the
# common prefix of the set of files, and for the Whitney format it is the
# single file.
DUST_MODELS = {
    "kmh94_3.1_hg": ("whitney", "kmh94_hg/kmh94_3.1_hg"),
    "kmh94_3.1_full": ("bhmie", "kmh94_full/kmh94_3.1_full/kmh94_3.1_full"),
    "d03_3.1_6.0_A": ("bhmie", "d03/d03_3.1_6.0_A/d03_3.1_6.0_A"),
    "d03_4.0_4.0_A": ("bhmie", "d03/d03_4.0_4.0_A/d03_4.0_4.0_A"),
    "d03_5.5_3.0_A": ("bhmie", "d03/d03_5.5_3.0_A/d03_5.5_3.0_A"),
}

SUBLIMATION_MODES = ("no", "fast", "slow", "cap")

# Wavelength range (in microns) that the optical properties are extrapolated
# to, so that the dust can be used with any source spectrum.
WAV_MIN = 1.0e-3
WAV_MAX = 1.0e7


def available_dust():
    """
    Return the names of the dust models that can be passed to `get_dust`.
    """
    return sorted(DUST_MODELS)


def _check_sublimation(sublimation_mode, sublimation_temperature):
    if sublimation_mode not in SUBLIMATION_MODES:
        raise ValueError(
            f"sublimation_mode should be one of {'/'.join(SUBLIMATION_MODES)}, "
            f"got {sublimation_mode!r}"
        )
    if sublimation_mode == "no":
        if sublimation_temperature is not None:
            raise ValueError(
                "sublimation_temperature was given but sublimation_mode is 'no'"
            )
    elif sublimation_temperature is None:
        raise ValueError(
            f"sublimation_temperature is required when sublimation_mode is "
            f"{sublimation_mode!r}"
        )


def get_dust(name, sublimation_mode="no", sublimation_temperature=None):
    """
    Build one of the dust models in the library.

    Parameters
    ----------
    name : str
        The name of the dust model, one of the values returned by
        `available_dust`.
    sublimation_mode : {'no', 'fast', 'slow', 'cap'}, optional
        The dust sublimation mode, as defined by
        ``SphericalDust.set_sublimation_temperature`` in Hyperion.
    sublimation_temperature : float, optional
        The dust sublimation temperature in K. This is required unless
        ``sublimation_mode`` is ``'no'``.

    Returns
    -------
    dust : `hyperion.dust.SphericalDust`
        The dust object, which can be assigned to a density component of a
        Hyperion model directly.
    """

    from hyperion.dust import BHDust, TTsreDust

    if name not in DUST_MODELS:
        raise ValueError(
            f"Unknown dust model {name!r}, should be one of "
            f"{', '.join(available_dust())}"
        )

    _check_sublimation(sublimation_mode, sublimation_temperature)

    kind, location = DUST_MODELS[name]
    path = os.path.join(DATA_DIR, *location.split("/"))

    dust = BHDust(path) if kind == "bhmie" else TTsreDust(path)
    dust.optical_properties.extrapolate_wav(WAV_MIN, WAV_MAX)

    if sublimation_mode != "no":
        dust.set_sublimation_temperature(
            sublimation_mode, temperature=sublimation_temperature
        )

    return dust


def _package_version(package):
    try:
        return version(package)
    except PackageNotFoundError:
        return "unknown"


def _default_cache_dir():
    from astropy.config import get_cache_dir

    return get_cache_dir("hyperion_dust")


def get_dust_filename(
    name, sublimation_mode="no", sublimation_temperature=None, cache_dir=None
):
    """
    Return the path to a Hyperion HDF5 dust file for one of the dust models
    in the library, generating the file if it does not exist yet.

    The files are generated from the tables included in this package the
    first time they are requested, then re-used. They are kept separately
    for each version of this package and of Hyperion, so upgrading either
    will cause the files to be generated again.

    The version of this package is stored in the ``hyperion_dust_version``
    attribute of the file. This is not the case for dust objects returned by
    `get_dust` that are then written out with Hyperion.

    Parameters
    ----------
    name : str
        The name of the dust model, one of the values returned by
        `available_dust`.
    sublimation_mode : {'no', 'fast', 'slow', 'cap'}, optional
        The dust sublimation mode, as defined by
        ``SphericalDust.set_sublimation_temperature`` in Hyperion.
    sublimation_temperature : float, optional
        The dust sublimation temperature in K. This is required unless
        ``sublimation_mode`` is ``'no'``.
    cache_dir : str, optional
        The directory in which to look for and write the file. This
        defaults to a ``hyperion_dust`` directory inside the astropy cache
        directory.

    Returns
    -------
    filename : str
        The path to the HDF5 dust file.
    """

    if name not in DUST_MODELS:
        raise ValueError(
            f"Unknown dust model {name!r}, should be one of "
            f"{', '.join(available_dust())}"
        )

    _check_sublimation(sublimation_mode, sublimation_temperature)

    if cache_dir is None:
        cache_dir = _default_cache_dir()

    cache_dir = os.path.join(
        cache_dir,
        f"{_package_version('hyperion-dust')}_hyperion-{_package_version('hyperion')}",
    )

    if sublimation_mode == "no":
        basename = f"{name}.hdf5"
    else:
        basename = f"{name}_sub_{sublimation_mode}_{float(sublimation_temperature)!r}K.hdf5"

    filename = os.path.join(cache_dir, basename)

    if os.path.exists(filename):
        return filename

    import h5py
    import numpy as np

    dust = get_dust(
        name,
        sublimation_mode=sublimation_mode,
        sublimation_temperature=sublimation_temperature,
    )

    # Write to a temporary file in the same directory then rename, so that a
    # partially written file is never picked up, including by another
    # process requesting the same dust at the same time.
    os.makedirs(cache_dir, exist_ok=True)
    handle, temporary = tempfile.mkstemp(suffix=".hdf5", dir=cache_dir)
    os.close(handle)
    try:
        dust.write(temporary)
        # Record which version of the tables the file was generated from
        # (Hyperion records its own version in python_version)
        with h5py.File(temporary, "r+") as f:
            f.attrs["hyperion_dust_version"] = np.bytes_(
                _package_version("hyperion-dust")
            )
        os.replace(temporary, filename)
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)

    return filename
