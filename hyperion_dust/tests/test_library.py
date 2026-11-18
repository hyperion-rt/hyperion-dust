import os

import h5py
import numpy as np
import pytest
from hyperion.dust import SphericalDust

from hyperion_dust import available_dust, get_dust, get_dust_filename

C_MICRON = 2.99792458e14


def albedo_at(dust, wav):
    nu = dust.optical_properties.nu
    albedo = dust.optical_properties.albedo
    order = np.argsort(nu)
    return np.interp(C_MICRON / wav, nu[order], albedo[order])


def test_available_dust():
    assert available_dust() == [
        "d03_3.1_6.0_A",
        "d03_4.0_4.0_A",
        "d03_5.5_3.0_A",
        "kmh94_3.1_full",
        "kmh94_3.1_hg",
    ]


@pytest.mark.parametrize("name", available_dust())
def test_get_dust(name):
    dust = get_dust(name)
    assert isinstance(dust, SphericalDust)
    wav = C_MICRON / dust.optical_properties.nu
    assert wav.min() <= 1.0e-3
    assert wav.max() >= 1.0e7
    assert np.all(dust.optical_properties.albedo >= 0)
    assert np.all(dust.optical_properties.albedo <= 1)
    assert dust.sublimation_mode == "no"


# Albedo published by Draine for the R_V=5.5 model. The tables computed with
# a version of bhmie that had a bug gave very different values (0.89, 0.56
# and 0.08), so this guards against those tables being picked up again.
@pytest.mark.parametrize(
    ("wav", "albedo"), [(0.55, 0.72), (2.2, 0.53), (4.8, 0.334)]
)
def test_d03_albedo(wav, albedo):
    dust = get_dust("d03_5.5_3.0_A")
    assert albedo_at(dust, wav) == pytest.approx(albedo, abs=0.01)


def test_get_dust_sublimation():
    dust = get_dust(
        "d03_5.5_3.0_A", sublimation_mode="fast", sublimation_temperature=1600.0
    )
    assert dust.sublimation_mode == "fast"
    assert dust.temperature2specific_energy(1600.0) == pytest.approx(
        dust.sublimation_energy
    )


def test_get_dust_invalid():
    with pytest.raises(ValueError, match="Unknown dust model"):
        get_dust("spam")
    with pytest.raises(ValueError, match="sublimation_mode should be one of"):
        get_dust("d03_5.5_3.0_A", sublimation_mode="spam")
    with pytest.raises(ValueError, match="sublimation_temperature is required"):
        get_dust("d03_5.5_3.0_A", sublimation_mode="fast")
    with pytest.raises(ValueError, match="sublimation_mode is 'no'"):
        get_dust("d03_5.5_3.0_A", sublimation_temperature=1600.0)


def test_get_dust_filename(tmp_path):
    filename = get_dust_filename("kmh94_3.1_hg", cache_dir=str(tmp_path))
    assert os.path.basename(filename) == "kmh94_3.1_hg.hdf5"
    assert os.path.dirname(os.path.dirname(filename)) == str(tmp_path)

    # Only the final file should be left behind
    assert os.listdir(os.path.dirname(filename)) == ["kmh94_3.1_hg.hdf5"]

    with h5py.File(filename, "r") as f:
        assert f.attrs["sublimation_mode"] == b"no"
        assert "optical_properties" in f
        assert "emissivities" in f

    dust = SphericalDust(filename)
    reference = get_dust("kmh94_3.1_hg")
    np.testing.assert_allclose(
        dust.optical_properties.chi, reference.optical_properties.chi
    )
    np.testing.assert_allclose(
        dust.optical_properties.albedo, reference.optical_properties.albedo
    )


def test_get_dust_filename_cached(tmp_path):
    filename = get_dust_filename("kmh94_3.1_hg", cache_dir=str(tmp_path))
    modified = os.stat(filename).st_mtime_ns
    assert get_dust_filename("kmh94_3.1_hg", cache_dir=str(tmp_path)) == filename
    assert os.stat(filename).st_mtime_ns == modified


def test_get_dust_filename_sublimation(tmp_path):
    plain = get_dust_filename("d03_5.5_3.0_A", cache_dir=str(tmp_path))
    fast = get_dust_filename(
        "d03_5.5_3.0_A",
        sublimation_mode="fast",
        sublimation_temperature=1600,
        cache_dir=str(tmp_path),
    )
    slow = get_dust_filename(
        "d03_5.5_3.0_A",
        sublimation_mode="slow",
        sublimation_temperature=1600,
        cache_dir=str(tmp_path),
    )
    cooler = get_dust_filename(
        "d03_5.5_3.0_A",
        sublimation_mode="fast",
        sublimation_temperature=1500,
        cache_dir=str(tmp_path),
    )
    assert len({plain, fast, slow, cooler}) == 4

    with h5py.File(fast, "r") as f:
        assert f.attrs["sublimation_mode"] == b"fast"
        energy_1600 = f.attrs["sublimation_specific_energy"]
    with h5py.File(cooler, "r") as f:
        assert f.attrs["sublimation_specific_energy"] < energy_1600


def test_get_dust_filename_invalid(tmp_path):
    with pytest.raises(ValueError, match="Unknown dust model"):
        get_dust_filename("spam", cache_dir=str(tmp_path))
    with pytest.raises(ValueError, match="sublimation_temperature is required"):
        get_dust_filename(
            "d03_5.5_3.0_A", sublimation_mode="fast", cache_dir=str(tmp_path)
        )
    assert os.listdir(str(tmp_path)) == []
