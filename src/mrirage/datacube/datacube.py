import warnings
from typing import Iterable, Optional, Union

import numpy as np
from scipy.ndimage import gaussian_filter


class Datacube:
    """
    Utility class for storing 3D voxel images and affine matrices.

    Provides pass through functions for numpy operations on the image.
    """

    def __init__(
        self,
        image: np.ndarray,
        affine: np.ndarray,
        affine_inv: Optional[np.ndarray] = None,
    ):
        """
        Args:
            image: 3D voxel image
            affine: affine matrix
            affine_inv: inverse of affine matrix (optional, will be computed if not provided)
        """
        assert image.ndim == 3, "Datacube must be 3D"
        self.image = image
        self.affine = affine
        self.affine_inv = (
            np.linalg.inv(self.affine) if affine_inv is None else affine_inv
        )

    def transform(self, p: Union[np.ndarray, Iterable]):
        """
        Local space -> world space
        """
        return np.dot(self.affine, p)  # type: ignore

    def transform_inv(self, p: Union[np.ndarray, Iterable]):
        """
        World space -> local space
        """
        return np.dot(self.affine_inv, p)  # type: ignore

    def apply_gaussian(
        self, sigma: Union[int, float, complex, Iterable], truncate: float = 4.0
    ):
        self.image = gaussian_filter(self.image, sigma=sigma, truncate=truncate)
        return self

    def apply(self, fun):
        self.image = fun(self.image)
        return self

    def normalize(self, min_value=0.0, max_value=1.0):
        amin = np.min(self.image)
        amax = np.max(self.image)
        arange = amax - amin
        if arange == 0:
            warnings.warn("Could not normalize datacube (zero range).")
            return self
        self.image = ((self.image - amin) / arange) * max_value + min_value
        return self

    def __lt__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError()
        return Datacube(
            (self.image.__lt__(other)).astype(self.image.dtype),
            self.affine,
            self.affine_inv,
        )

    def __le__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError()
        return Datacube(
            (self.image.__le__(other)).astype(self.image.dtype),
            self.affine,
            self.affine_inv,
        )

    def __gt__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError()
        return Datacube(
            (self.image.__gt__(other)).astype(self.image.dtype),
            self.affine,
            self.affine_inv,
        )

    def __ge__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError()
        return Datacube(
            (self.image.__ge__(other)).astype(self.image.dtype),
            self.affine,
            self.affine_inv,
        )

    def __eq__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError()
        return Datacube(
            (self.image.__eq__(other)).astype(self.image.dtype),
            self.affine,
            self.affine_inv,
        )

    def __ne__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError()
        return Datacube(
            (self.image.__ne__(other)).astype(self.image.dtype),
            self.affine,
            self.affine_inv,
        )

    def __abs__(self):
        return Datacube(abs(self.image), self.affine, self.affine_inv)

    def __add__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError()
        return Datacube((self.image.__add__(other)), self.affine, self.affine_inv)

    def __sub__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError()
        return Datacube((self.image.__sub__(other)), self.affine, self.affine_inv)

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError()
        return Datacube((self.image.__mul__(other)), self.affine, self.affine_inv)

    def __pow__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError()
        return Datacube((self.image.__pow__(other)), self.affine, self.affine_inv)

    def __truediv__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError()
        return Datacube((self.image.__truediv__(other)), self.affine, self.affine_inv)

    def __floordiv__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError()
        return Datacube((self.image.__floordiv__(other)), self.affine, self.affine_inv)

    def __mod__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError()
        return Datacube((self.image.__mod__(other)), self.affine, self.affine_inv)
