from typing import Any, Union

import nibabel as nib
from nibabel.spatialimages import SpatialImage as NibabelImage

from ..datacube.datacube import Datacube


def get_nifti_cube(image: Union[str, Any]):
    if isinstance(image, str):
        img = nib.nifti1.load(image)
        return Datacube(img.get_fdata(caching="unchanged"), img.affine)
    if isinstance(image, NibabelImage):
        # noinspection PyTypeChecker
        return Datacube(image.get_fdata(), image.affine)
    return image
