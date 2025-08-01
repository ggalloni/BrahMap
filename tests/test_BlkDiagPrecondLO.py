############################ TEST DESCRIPTION ############################
#
# Test defined here are related to the `BlockDiagonalPreconditionerLO` of BrahMap.
# Analogous to this class, in the test suite, we have defined another version of `BlockDiagonalPreconditionerLO` based on only the python routines.
#
# - class `TestBlkDiagPrecondLO_I_Cpp`:
#
#   -   `test_I_cpp`: tests whether `mult` and `rmult` method overloads of
# the two versions of `BlkDiagPrecondLO_tools.BDPLO_mult_I()` produce the
# same result
#
# - Same as above, but for QU and IQU
#
# - class `TestBlkDiagPrecondLO_I`:
#
#   -   `test_I`: The matrix view of the operator
# `brahmap.interfaces.BlockDiagonalPreconditionerLO` is a block matrix.
# In this test, we first compute the matrix view of the operator and then
# compare the elements of each block (corresponding to a given pixel) with
# their explicit computations
#
# - Same as above, but for QU and IQU
#
###########################################################################

import pytest
import numpy as np

import brahmap

import py_BlkDiagPrecondLO as bdplo
import py_ProcessTimeSamples as hpts


class InitCommonParams:
    np.random.seed(6534 + brahmap.MPI_UTILS.rank)
    npix = 128
    nsamples_global = npix * 6

    div, rem = divmod(nsamples_global, brahmap.MPI_UTILS.size)
    nsamples = div + (brahmap.MPI_UTILS.rank < rem)

    nbad_pixels_global = npix
    div, rem = divmod(nbad_pixels_global, brahmap.MPI_UTILS.size)
    nbad_pixels = div + (brahmap.MPI_UTILS.rank < rem)

    pointings_flag = np.ones(nsamples, dtype=bool)
    bad_samples = np.random.randint(low=0, high=nsamples, size=nbad_pixels)
    pointings_flag[bad_samples] = False


class InitInt32Params(InitCommonParams):
    def __init__(self) -> None:
        super().__init__()

        self.dtype = np.int32
        self.pointings = np.random.randint(
            low=0, high=self.npix, size=self.nsamples, dtype=self.dtype
        )


class InitInt64Params(InitCommonParams):
    def __init__(self) -> None:
        super().__init__()

        self.dtype = np.int64
        self.pointings = np.random.randint(
            low=0, high=self.npix, size=self.nsamples, dtype=self.dtype
        )


class InitFloat32Params(InitCommonParams):
    def __init__(self) -> None:
        super().__init__()

        self.dtype = np.float32
        self.noise_weights = np.random.random(size=self.nsamples).astype(
            dtype=self.dtype
        )
        self.pol_angles = np.random.uniform(
            low=-np.pi / 2.0, high=np.pi / 2.0, size=self.nsamples
        ).astype(dtype=self.dtype)


class InitFloat64Params(InitCommonParams):
    def __init__(self) -> None:
        super().__init__()

        self.dtype = np.float64
        self.noise_weights = np.random.random(size=self.nsamples).astype(
            dtype=self.dtype
        )
        self.pol_angles = np.random.uniform(
            low=-np.pi / 2.0, high=np.pi / 2.0, size=self.nsamples
        ).astype(dtype=self.dtype)


# Initializing the parameter classes
initint32 = InitInt32Params()
initint64 = InitInt64Params()
initfloat32 = InitFloat32Params()
initfloat64 = InitFloat64Params()


@pytest.mark.parametrize(
    "initint, initfloat, rtol, atol",
    [
        (initint32, initfloat32, 1.5e-4, 1.0e-5),
        (initint64, initfloat32, 1.5e-4, 1.0e-5),
        (initint32, initfloat64, 1.5e-5, 1.0e-10),
        (initint64, initfloat64, 1.5e-5, 1.0e-10),
    ],
)
class TestBlkDiagPrecondLO_I_Cpp(InitCommonParams):
    def test_I_cpp(self, initint, initfloat, rtol, atol):
        solver_type = hpts.SolverType.I

        PTS = hpts.ProcessTimeSamples(
            npix=self.npix,
            pointings=initint.pointings,
            pointings_flag=self.pointings_flag,
            solver_type=solver_type,
            noise_weights=initfloat.noise_weights,
            dtype_float=initfloat.dtype,
            update_pointings_inplace=False,
        )
        BDP_cpp = brahmap.core.BlockDiagonalPreconditionerLO(PTS)
        BDP_py = bdplo.BlockDiagonalPreconditionerLO(PTS)

        vec = np.random.random(PTS.new_npix * PTS.solver_type).astype(
            dtype=initfloat.dtype, copy=False
        )

        cpp_prod = BDP_cpp * vec

        py_prod = BDP_py * vec

        np.testing.assert_allclose(cpp_prod, py_prod, rtol=rtol, atol=atol)


@pytest.mark.parametrize(
    "initint, initfloat, rtol, atol",
    [
        (initint32, initfloat32, 1.5e-4, 1.0e-5),
        (initint64, initfloat32, 1.5e-4, 1.0e-5),
        (initint32, initfloat64, 1.5e-5, 1.0e-10),
        (initint64, initfloat64, 1.5e-5, 1.0e-10),
    ],
)
class TestBlkDiagPrecondLO_QU_Cpp(InitCommonParams):
    def test_QU_cpp(self, initint, initfloat, rtol, atol):
        solver_type = hpts.SolverType.QU

        PTS = hpts.ProcessTimeSamples(
            npix=self.npix,
            pointings=initint.pointings,
            pointings_flag=self.pointings_flag,
            solver_type=solver_type,
            pol_angles=initfloat.pol_angles,
            noise_weights=initfloat.noise_weights,
            dtype_float=initfloat.dtype,
            update_pointings_inplace=False,
        )
        BDP_cpp = brahmap.core.BlockDiagonalPreconditionerLO(PTS)
        BDP_py = bdplo.BlockDiagonalPreconditionerLO(PTS)

        vec = np.random.random(PTS.new_npix * PTS.solver_type).astype(
            dtype=initfloat.dtype, copy=False
        )

        cpp_prod = BDP_cpp * vec

        py_prod = BDP_py * vec

        np.testing.assert_allclose(cpp_prod, py_prod, rtol=rtol, atol=atol)


@pytest.mark.parametrize(
    "initint, initfloat, rtol, atol",
    [
        (initint32, initfloat32, 1.5e-4, 1.0e-5),
        (initint64, initfloat32, 1.5e-4, 1.0e-5),
        (initint32, initfloat64, 1.5e-5, 1.0e-10),
        (initint64, initfloat64, 1.5e-5, 1.0e-10),
    ],
)
class TestBlkDiagPrecondLO_IQU_Cpp(InitCommonParams):
    def test_IQU_cpp(self, initint, initfloat, rtol, atol):
        solver_type = hpts.SolverType.IQU

        PTS = hpts.ProcessTimeSamples(
            npix=self.npix,
            pointings=initint.pointings,
            pointings_flag=self.pointings_flag,
            solver_type=solver_type,
            pol_angles=initfloat.pol_angles,
            noise_weights=initfloat.noise_weights,
            dtype_float=initfloat.dtype,
            update_pointings_inplace=False,
        )
        BDP_cpp = brahmap.core.BlockDiagonalPreconditionerLO(PTS)
        BDP_py = bdplo.BlockDiagonalPreconditionerLO(PTS)

        vec = np.random.random(PTS.new_npix * PTS.solver_type).astype(
            dtype=initfloat.dtype, copy=False
        )

        cpp_prod = BDP_cpp * vec

        py_prod = BDP_py * vec

        np.testing.assert_allclose(cpp_prod, py_prod, rtol=rtol, atol=atol)


@pytest.mark.parametrize(
    "initint, initfloat, rtol, atol",
    [
        (initint32, initfloat32, 1.5e-4, 1.0e-5),
        (initint64, initfloat32, 1.5e-4, 1.0e-5),
        (initint32, initfloat64, 1.5e-5, 1.0e-10),
        (initint64, initfloat64, 1.5e-5, 1.0e-10),
    ],
)
class TestBlkDiagPrecondLO_I(InitCommonParams):
    def test_I(self, initint, initfloat, rtol, atol):
        solver_type = hpts.SolverType.I

        PTS = hpts.ProcessTimeSamples(
            npix=self.npix,
            pointings=initint.pointings,
            pointings_flag=self.pointings_flag,
            solver_type=solver_type,
            noise_weights=initfloat.noise_weights,
            dtype_float=initfloat.dtype,
            update_pointings_inplace=False,
        )
        BDP = brahmap.core.BlockDiagonalPreconditionerLO(PTS)

        bdp_array = BDP.to_array()
        diag_inv_count = np.diag(1.0 / PTS.weighted_counts)

        np.testing.assert_allclose(bdp_array, diag_inv_count, rtol=rtol, atol=atol)


@pytest.mark.parametrize(
    "initint, initfloat, rtol, atol",
    [
        (initint32, initfloat32, 1.5e-3, 1.0e-5),
        (initint64, initfloat32, 1.5e-3, 1.0e-5),
        (initint32, initfloat64, 1.5e-5, 1.0e-10),
        (initint64, initfloat64, 1.5e-5, 1.0e-10),
    ],
)
class TestBlkDiagPrecondLO_QU(InitCommonParams):
    def test_QU(self, initint, initfloat, rtol, atol):
        solver_type = hpts.SolverType.QU

        PTS = hpts.ProcessTimeSamples(
            npix=self.npix,
            pointings=initint.pointings,
            pointings_flag=self.pointings_flag,
            solver_type=solver_type,
            pol_angles=initfloat.pol_angles,
            noise_weights=initfloat.noise_weights,
            dtype_float=initfloat.dtype,
            update_pointings_inplace=False,
        )
        BDP = brahmap.core.BlockDiagonalPreconditionerLO(PTS)

        bdp_matrix = BDP.to_array()

        bdp_test_matrix = np.zeros(
            (PTS.new_npix * PTS.solver_type, PTS.new_npix * PTS.solver_type),
            dtype=initfloat.dtype,
        )

        for idx in range(PTS.new_npix):
            block_matrix = np.zeros((2, 2), dtype=initfloat.dtype)
            block_matrix[0, 0] = PTS.weighted_cos_sq[idx]
            block_matrix[0, 1] = PTS.weighted_sincos[idx]
            block_matrix[1, 0] = PTS.weighted_sincos[idx]
            block_matrix[1, 1] = PTS.weighted_sin_sq[idx]
            block_inv = np.linalg.inv(block_matrix)

            bdp_test_matrix[
                idx * 2 : (idx + 1) * 2, idx * 2 : (idx + 1) * 2
            ] = block_inv

        np.testing.assert_allclose(bdp_matrix, bdp_test_matrix, rtol=rtol, atol=atol)


@pytest.mark.parametrize(
    "initint, initfloat, rtol, atol",
    [
        (initint32, initfloat32, 1.0e-3, 1.0e-5),
        (initint64, initfloat32, 1.0e-3, 1.0e-5),
        (initint32, initfloat64, 1.5e-5, 1.0e-10),
        (initint64, initfloat64, 1.5e-5, 1.0e-10),
    ],
)
class TestBlkDiagPrecondLO_IQU(InitCommonParams):
    def test_IQU(self, initint, initfloat, rtol, atol):
        solver_type = hpts.SolverType.IQU

        PTS = hpts.ProcessTimeSamples(
            npix=self.npix,
            pointings=initint.pointings,
            pointings_flag=self.pointings_flag,
            solver_type=solver_type,
            pol_angles=initfloat.pol_angles,
            noise_weights=initfloat.noise_weights,
            dtype_float=initfloat.dtype,
            update_pointings_inplace=False,
        )
        BDP = brahmap.core.BlockDiagonalPreconditionerLO(PTS)

        bdp_matrix = BDP.to_array()

        bdp_test_matrix = np.zeros(
            (PTS.new_npix * PTS.solver_type, PTS.new_npix * PTS.solver_type),
            dtype=initfloat.dtype,
        )

        for idx in range(PTS.new_npix):
            block_matrix = np.zeros((3, 3), dtype=initfloat.dtype)
            block_matrix[0, 0] = PTS.weighted_counts[idx]
            block_matrix[0, 1] = PTS.weighted_cos[idx]
            block_matrix[0, 2] = PTS.weighted_sin[idx]
            block_matrix[1, 0] = PTS.weighted_cos[idx]
            block_matrix[1, 1] = PTS.weighted_cos_sq[idx]
            block_matrix[1, 2] = PTS.weighted_sincos[idx]
            block_matrix[2, 0] = PTS.weighted_sin[idx]
            block_matrix[2, 1] = PTS.weighted_sincos[idx]
            block_matrix[2, 2] = PTS.weighted_sin_sq[idx]
            block_inv = np.linalg.inv(block_matrix)

            bdp_test_matrix[
                idx * 3 : (idx + 1) * 3, idx * 3 : (idx + 1) * 3
            ] = block_inv

        np.testing.assert_allclose(bdp_matrix, bdp_test_matrix, rtol=rtol, atol=atol)


if __name__ == "__main__":
    pytest.main(
        [
            f"{__file__}::TestBlkDiagPrecondLO_I_Cpp::test_I_cpp",
            "-v",
            "-s",
        ]
    )
    pytest.main(
        [
            f"{__file__}::TestBlkDiagPrecondLO_QU_Cpp::test_QU_cpp",
            "-v",
            "-s",
        ]
    )
    pytest.main(
        [
            f"{__file__}::TestBlkDiagPrecondLO_IQU_Cpp::test_IQU_cpp",
            "-v",
            "-s",
        ]
    )

    pytest.main(
        [
            f"{__file__}::TestBlkDiagPrecondLO_I::test_I",
            "-v",
            "-s",
        ]
    )
    pytest.main(
        [
            f"{__file__}::TestBlkDiagPrecondLO_QU::test_QU",
            "-v",
            "-s",
        ]
    )
    pytest.main(
        [
            f"{__file__}::TestBlkDiagPrecondLO_IQU::test_IQU",
            "-v",
            "-s",
        ]
    )
