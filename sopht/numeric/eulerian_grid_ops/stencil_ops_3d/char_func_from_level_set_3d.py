"""Kernels for computing characteristic function from level set field in 3D."""
import numpy as np

import pystencils as ps

import sympy as sp


def gen_char_func_from_level_set_via_sine_heaviside_pyst_kernel_3d(
    blend_width,
    real_t,
    num_threads=False,
    fixed_grid_size=False,
):
    """Level set --> Characteristic function 3D kernel generator.

    Generate function that computes characteristic function field
    from the level set field, via a smooth sine Heaviside function.
    """
    pyst_dtype = "float32" if real_t == np.float32 else "float64"
    grid_info = (
        f"{fixed_grid_size[0]}, {fixed_grid_size[1]}, {fixed_grid_size[2]}"
        if fixed_grid_size
        else "3D"
    )
    kernel_config = ps.CreateKernelConfig(
        data_type=pyst_dtype,
        default_number_float=pyst_dtype,
        cpu_openmp=num_threads,
    )
    sine_prefactor = np.pi / blend_width

    @ps.kernel
    def _char_func_from_level_set_via_sine_heaviside_stencil_3d():
        char_func_field, level_set_field = ps.fields(
            f"char_func_field, level_set_field : {pyst_dtype}[{grid_info}]"
        )
        char_func_field[0, 0, 0] @= (
            1 if (level_set_field[0, 0, 0] > blend_width) else 0
        ) + (
            0
            if abs(level_set_field[0, 0, 0]) > blend_width
            else 0.5
            * (
                1
                + level_set_field[0, 0, 0] / blend_width
                + sp.sin(sine_prefactor * level_set_field[0, 0, 0]) / np.pi
            )
        )

    char_func_from_level_set_via_sine_heaviside_pyst_kernel_3d = ps.create_kernel(
        _char_func_from_level_set_via_sine_heaviside_stencil_3d,
        config=kernel_config,
    ).compile()
    return char_func_from_level_set_via_sine_heaviside_pyst_kernel_3d
