from typing import TypeVar, Union

import nibabel as nib
from nibabel.spatialimages import SpatialImage as NibabelImage

from ..datacube.datacube import Datacube

T = TypeVar("T")


def get_nifti_cube(image: Union[str, NibabelImage, T]) -> Union[Datacube, T]:
    """
    Load a nifti image into a Datacube.

    Args:
        image: Image to load.

    Returns:
        Datacube containing the image.
    """
    if isinstance(image, str):
        img = nib.nifti1.load(image)
        return Datacube(img.get_fdata(caching="unchanged"), img.affine)
    if isinstance(image, NibabelImage):
        return Datacube(image.get_fdata(), image.affine)
    return image
