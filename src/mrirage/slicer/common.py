import numpy as np

RAS_SPACE_DIRECTIONS = np.array(
    [
        ["Left", "Right"],
        ["Posterior", "Anterior"],
        ["Inferior", "Superior"],
    ]
)
RAS_SPACE_LABELS = np.array(
    ["x Left-Right", "y Posterior-Anterior", "z Inferior-Superior"]
)
RAS_SPACE_LABELS_SHORT = np.array(["x (L-R)", "y (P-A)", "z (I-S)"])
