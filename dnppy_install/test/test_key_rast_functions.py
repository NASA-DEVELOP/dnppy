__author__ = 'jwely'


def test_key_rast_functions(test_dir):
    """
    Requires the test environment to have already been built.

    tests the following functions from the raster module:
        spatially_match
            cilp_and_snap
            project_resample
            enf_rastlist
                is_rast
        raster_overlap
            clip_and_snap
            null_define
            to_numpy
            from_numpy
        clip_to_shape
        grab_info
        null_define
        null_set_range

    And, by necessity, calls the following functions from MODIS
    """


