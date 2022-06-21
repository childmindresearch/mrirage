import numpy as np

from mrirage import Datacube, slicer


def test_slicer_scalar():
    cube = Datacube(
        image=np.reshape(np.arange(3 * 3 * 3, dtype=int), (3, 3, 3)),
        affine=np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=int)
    )

    assert slicer.value_at(cube, (0, 0, 0)) == 0
    assert slicer.value_at(cube, (1, 0, 0)) == 9
    assert slicer.value_at(cube, (0, 1, 0)) == 3
    assert slicer.value_at(cube, (0, 0, 1)) == 1


def test_slicer_2d():
    cube = Datacube(
        image=np.reshape(np.arange(3 * 3 * 3, dtype=np.float64), (3, 3, 3)),
        affine=np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float64)
    )

    rastered_0_0, axis_lims_0_0, _ = slicer.slice_image(cube, axis=0, axis_offset=0)
    rastered_0_1, axis_lims_0_1, _ = slicer.slice_image(cube, axis=0, axis_offset=1)
    rastered_1_0, axis_lims_1_0, _ = slicer.slice_image(cube, axis=1, axis_offset=0)
    rastered_2_0, axis_lims_2_0, _ = slicer.slice_image(cube, axis=2, axis_offset=0)

    assert np.allclose(rastered_0_0, np.array(
        [[0, 3, 6],
         [1, 4, 7],
         [2, 5, 8]]
    ))
    assert np.allclose(axis_lims_0_1, np.array(
        [[0, 2],
         [0, 2]]
    ))

    assert np.allclose(rastered_0_1, np.array(
        [[9, 12, 15],
         [10, 13, 16],
         [11, 14, 17]]
    ))
    assert np.allclose(rastered_1_0, np.array(
        [[0, 9, 18],
         [1, 10, 19],
         [2, 11, 20]]
    ))
    assert np.allclose(rastered_2_0, np.array(
        [[0, 9, 18],
         [3, 12, 21],
         [6, 15, 24]]
    ))
