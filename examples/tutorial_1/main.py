import mrirage as mir

PATH_MNI_T1 = "data/mni_icbm152_t1_tal_nlin_asym_09b_hires.nii"
PATH_MNI_MASK = "data/mni_icbm152_t1_tal_nlin_asym_09a_mask.nii"
PATH_STAT_MAP = "data/Q1_NC_vs_MIG.nii.gz"

comp = mir.quick_xyz(
    layers=[
        mir.LayerVoxel(
            data=PATH_MNI_T1,
            alpha_map=mir.get_nifti_cube(PATH_MNI_MASK)
            .apply_gaussian(sigma=2)
            .normalize(),
            color_scale=mir.ColorScaleFromName("Greys_r"),
            interp_screen="bicubic",
            legend=True,
            legend_label="Structure",
        ),
        mir.LayerVoxel(
            data=PATH_STAT_MAP,
            color_scale=mir.ColorScaleFromName("coolwarm", vmin=-3, vmax=3),
            alpha_map=lambda image: abs(image) > 1.8,
            legend=True,
            legend_label="NC vs MIG",
        ),
        mir.LayerCrossOrigin(
            style=mir.Style(color="black", alpha=0.6), padding_inner=4, legend=True
        ),
        mir.LayerCoordinate(),
    ],
    bounds=mir.bounds_mni_cube(),
    origin=(41, 47, 17),
)

comp.render_show()

if __name__ == "__main__":
    pass
