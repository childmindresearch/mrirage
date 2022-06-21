from .spoint import t_spoint_like, as_slicer_point
from ..datacube import Datacube


def value_at(data: Datacube, position: t_spoint_like):
    p = data.transform_inv(as_slicer_point(position)).astype(int)  # todo: interpolation
    return data.image[p[0], p[1], p[2]]
