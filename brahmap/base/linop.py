# Original code:
#
# Copyright (c) 2008-2013, Dominique Orban <dominique.orban@gerad.ca>
# All rights reserved.
#
# Copyright (c) 2013-2014, Ghislain Vaillant <ghisvail@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# 3. Neither the name of the linop developers nor the names of any contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
#
# Modified version:
#
# Copyright (c) 2023-present, Avinash Anand <avinash.anand@roma2.infn.it>
# and Giuseppe Puglisi
#
# This file is part of BrahMap.
#
# Licensed under the MIT License. See the <LICENSE.txt> file for details.


from typing import Callable, Optional, Tuple, Any
import numbers
import numpy as np
import numpy.typing as npt
import logging

from .misc import ShapeError


# Default (null) logger.
null_log = logging.getLogger("linop")
null_log.setLevel(logging.WARNING)
null_log.addHandler(logging.NullHandler())


class BaseLinearOperator(object):
    """Base class for defining the common interface shared by all linear
    operators.

    A linear operator is a linear mapping $x \\mapsto A(x)$ such that the size
    of the input vector $x$ is `nargin` and the size of the output vector is
    `nargout`. The linear operator $A$ can be visualized as a matrix of shape
    `(nargout, nargin)`.

    Parameters
    ----------
    nargin : int
        Size of the input vector $x$
    nargout : int
        Size of the output vector $A(x)$
    symmetric : bool, optional
        A parameter to specify whether the linear operator is symmetric, by
        default `False`
    dtype : npt.DTypeLike, optional
        Data type of the linear operator, by default `np.float64`
    **kwargs : Any
        Extra keywords arguments
    """

    # A logger may be attached to the linear operator via the `logger` keyword
    # argument.

    def __init__(
        self,
        nargin: int,
        nargout: int,
        symmetric: bool = False,
        dtype: npt.DTypeLike = np.float64,
        **kwargs,
    ):
        self.__nargin = nargin
        self.__nargout = nargout
        self.__symmetric = symmetric
        self.__shape = (nargout, nargin)
        self.dtype = dtype
        self._nMatvec = 0

        # Log activity.
        self.logger = kwargs.get("logger", null_log)
        self.logger.info("New linear operator with shape " + str(self.shape))
        return

    @property
    def nargin(self) -> int:
        """The size of the input vector."""
        return self.__nargin

    @property
    def nargout(self) -> int:
        """The size of the output vector."""
        return self.__nargout

    @property
    def symmetric(self) -> bool:
        """Indicate whether the operator is symmetric or not."""
        return self.__symmetric

    @property
    def shape(self) -> Tuple[int, int]:
        """The shape of the operator."""
        return self.__shape

    @property
    def dtype(self) -> npt.DTypeLike:
        """The data type of the operator."""
        return self.__dtype

    @dtype.setter
    def dtype(self, dtype):
        self.__dtype = dtype

    @property
    def nMatvec(self) -> int:
        """The number of products with vectors computed so far."""
        return self._nMatvec

    def reset_counters(self):
        """Reset operator/vector product counter to zero."""
        self._nMatvec = 0

    def dot(self, x):
        """Numpy-like dot() method."""
        return self.__mul__(x)

    def __call__(self, *args, **kwargs):
        # An alias for __mul__.
        return self.__mul__(*args, **kwargs)

    def __mul__(self, x):
        raise NotImplementedError("Please subclass to implement __mul__.")

    def __repr__(self) -> str:
        if self.symmetric:
            s = "Symmetric"
        else:
            s = "Unsymmetric"
        s += " <" + self.__class__.__name__ + ">"
        s += " of type %s" % self.dtype
        s += " with shape (%d,%d)" % (self.nargout, self.nargin)
        return s


class LinearOperator(BaseLinearOperator):
    """
    A generic linear operator class.

    A linear operator constructed from a matrix-vector multiplication `matvec`,
    $x \\mapsto A(x)=Ax$ and possibly with a transposed-matrix-vector
    operation `rmatvec`, $x \\mapsto A(x)=A^T x$. If `symmetric` is `True`,
    `rmatvec` is ignored. All other keyword arguments are passed directly to
    the superclass.

    Parameters
    ----------
    nargin : int
        Size of the input vector $x$
    nargout : int
        Size of the output vector $A(x)$
    matvec : Callable
        A function that defines the matrix-vector product $x \\mapsto A(x)=Ax$
    rmatvec : Optional[Callable], optional
        A function that defines the transposed-matrix-vector product
        $x \\mapsto A(x)=A^T x$, by default `None`
    **kwargs : Any
        Extra keywords arguments
    """

    def __init__(
        self,
        nargin: int,
        nargout: int,
        matvec: Callable,
        rmatvec: Optional[Callable] = None,
        **kwargs,
    ):
        super(LinearOperator, self).__init__(
            nargin,
            nargout,
            **kwargs,
        )
        adjoint_of = kwargs.get("adjoint_of", None) or kwargs.get("transpose_of", None)
        rmatvec = rmatvec or kwargs.get("matvec_transp", None)

        self.__matvec = matvec

        if self.symmetric:
            self.__H = self
        else:
            if adjoint_of is None:
                if rmatvec is not None:
                    # Create 'pointer' to transpose operator.
                    self.__H = LinearOperator(
                        nargout,
                        nargin,
                        matvec=rmatvec,
                        rmatvec=matvec,
                        adjoint_of=self,
                        **kwargs,
                    )
                else:
                    self.__H = None
            else:
                # Use operator supplied as transpose operator.
                if isinstance(adjoint_of, BaseLinearOperator):
                    self.__H = adjoint_of
                else:
                    msg = (
                        "kwarg adjoint_of / transpose_of must be of type"
                        " LinearOperator."
                    )
                    msg += " Got " + str(adjoint_of.__class__)
                    raise ValueError(msg)

    @property
    def T(self):
        """The transpose operator"""
        return self.__H

    @property
    def H(self):
        """The adjoint operator"""
        return self.__H

    def matvec(self, x):
        """
        Matrix-vector multiplication.

        The matvec property encapsulates the `matvec` routine specified at
        construct time, to ensure the consistency of the input and output
        arrays with the operator's shape.
        """
        x = np.asanyarray(x)
        M, N = self.shape

        # check input data consistency
        N = int(N)
        try:
            x = x.reshape(N)
        except ValueError:
            msg = (
                "The size of the input array is incompatible with the "
                "operator dimensions\n"
                f"size of the input array: {len(x)}\n"
                f"shape of the operator: {self.shape}"
            )
            raise ValueError(msg)

        y = self.__matvec(x)

        # check output data consistency
        M = int(M)
        try:
            y = y.reshape(M)
        except ValueError:
            msg = (
                "The size of the output array is incompatible with the "
                "operator dimensions\n"
                f"size of the output array: {len(y)}\n"
                f"shape of the operator: {self.shape}"
            )
            raise ValueError(msg)

        return y

    def to_array(self) -> np.ndarray:
        """Returns the dense form of the linear operator as a 2D NumPy array

        !!! Warning

            This method first allocates a NumPy array of shape `self.shape`
            and data-type `self.dtype`, and then fills them with numbers. As
            such it can occupy an enormous amount of memory. Don't use it
            unless you understand the risk!
        """
        n, m = self.shape
        H = np.empty((n, m), dtype=self.dtype)
        ej = np.zeros(m, dtype=self.dtype)
        for j in range(m):
            ej[j] = 1.0
            H[:, j] = self * ej
            ej[j] = 0.0
        return H

    def __mul_scalar(self, x):
        # Product between a linear operator and a scalar
        result_type = np.result_type(self.dtype, type(x))

        if x != 0:

            def matvec(y):
                return x * (self(y))

            def rmatvec(y):
                return x * (self.H(y))

            return LinearOperator(
                self.nargin,
                self.nargout,
                symmetric=self.symmetric,
                matvec=matvec,
                rmatvec=rmatvec,
                dtype=result_type,
            )
        else:
            return ZeroOperator(self.nargin, self.nargout, dtype=result_type)

    def __mul_linop(self, op):
        # Product between two linear operators
        if self.nargin != op.nargout:
            msg = (
                "Cannot multiply the two operators together\n"
                f"shape of the first operator: {self.shape}\n"
                f"shape of the second operator: {op.shape}"
            )
            raise ShapeError(msg)

        def matvec(x):
            return self(op(x))

        def rmatvec(x):
            return op.T(self.H(x))

        result_type = np.result_type(self.dtype, op.dtype)

        return LinearOperator(
            op.nargin,
            self.nargout,
            symmetric=False,  # Generally.
            matvec=matvec,
            rmatvec=rmatvec,
            dtype=result_type,
        )

    def __mul_vector(self, x):
        # Product between a linear operator and a vector
        self._nMatvec += 1
        result_type = np.result_type(self.dtype, x.dtype)
        return self.matvec(x).astype(result_type, copy=False)

    def __mul__(self, x):
        # Returns a linear operator if x is a scalar or a linear operator
        # Returns a vector if x is an array
        if isinstance(x, numbers.Number):
            return self.__mul_scalar(x)
        elif isinstance(x, BaseLinearOperator):
            return self.__mul_linop(x)
        elif isinstance(x, np.ndarray):
            return self.__mul_vector(x)
        else:
            raise ValueError("Invalid multiplier! Cannot multiply")

    def __rmul__(self, x):
        if np.isscalar(x):
            return self.__mul__(x)
        raise ValueError("Invalid operation! Cannot multiply")

    def __add__(self, other):
        if not isinstance(other, BaseLinearOperator):
            raise ValueError("Invalid operation! Cannot add")
        if self.shape != other.shape:
            msg = (
                "Cannot add the two operators together\n"
                f"shape of the first operator: {self.shape}\n"
                f"shape of the second operator: {other.shape}"
            )
            raise ShapeError(msg)

        def matvec(x):
            return self(x) + other(x)

        def rmatvec(x):
            return self.H(x) + other.T(x)

        result_type = np.result_type(self.dtype, other.dtype)

        return LinearOperator(
            self.nargin,
            self.nargout,
            symmetric=self.symmetric and other.symmetric,
            matvec=matvec,
            rmatvec=rmatvec,
            dtype=result_type,
        )

    def __neg__(self):
        return self * (-1)

    def __sub__(self, other):
        if not isinstance(other, BaseLinearOperator):
            raise ValueError("Invalid operation! Cannot subtract")
        if self.shape != other.shape:
            msg = (
                "Cannot subtract one operator from the other\n"
                f"shape of the first operator: {self.shape}\n"
                f"shape of the second operator: {other.shape}"
            )
            raise ShapeError(msg)

        def matvec(x):
            return self(x) - other(x)

        def rmatvec(x):
            return self.H(x) - other.T(x)

        result_type = np.result_type(self.dtype, other.dtype)

        return LinearOperator(
            self.nargin,
            self.nargout,
            symmetric=self.symmetric and other.symmetric,
            matvec=matvec,
            rmatvec=rmatvec,
            dtype=result_type,
        )

    def __truediv__(self, other):
        if np.isscalar(other):
            return self * (1 / other)
        else:
            raise ValueError("Invalid operation! Cannot divide")

    def __pow__(self, other):
        if not isinstance(other, int):
            raise ValueError("Can only raise to integer power")
        if other < 0:
            raise ValueError("Can only raise to nonnegative power")
        if self.nargin != self.nargout:
            raise ShapeError("Can only raise square operators to a power")
        if other == 0:
            return IdentityOperator(self.nargin)
        if other == 1:
            return self
        return self * self ** (other - 1)


class IdentityOperator(LinearOperator):
    """A linear operator for the identity matrix of size `nargin`

    Parameters
    ----------
    nargin : int
        _description_
    **kwargs: Any
        _description_
    """

    def __init__(self, nargin: int, **kwargs: Any):
        if "symmetric" in kwargs:
            kwargs.pop("symmetric")
        if "matvec" in kwargs:
            kwargs.pop("matvec")

        super(IdentityOperator, self).__init__(
            nargin, nargin, symmetric=True, matvec=lambda x: x, **kwargs
        )


class DiagonalOperator(LinearOperator):
    """A linear operator for a diagonal matrix

    Parameters
    ----------
    diag : np.ndarray
        _description_
    **kwargs: Any
        _description_
    """

    def __init__(self, diag: np.ndarray, **kwargs: Any):
        if "symmetric" in kwargs:
            kwargs.pop("symmetric")
        if "matvec" in kwargs:
            kwargs.pop("matvec")
        if "dtype" in kwargs:
            kwargs.pop("dtype")

        self.diag = np.asarray(diag)
        if self.diag.ndim != 1:
            msg = "diag array must be 1-d"
            raise ValueError(msg)

        super(DiagonalOperator, self).__init__(
            self.diag.shape[0],
            self.diag.shape[0],
            symmetric=True,
            matvec=lambda x: self.diag * x,
            dtype=self.diag.dtype,
            **kwargs,
        )


class MatrixLinearOperator(LinearOperator):
    """A linear operator for a numpy matrix

    A linear operator wrapping the multiplication with a matrix and its
    transpose (real) or conjugate transpose (complex). The operator's dtype
    is the same as the specified `matrix` argument.

    Parameters
    ----------
    matrix : np.ndarray
        _description_
    **kwargs: Any
        _description_
    """

    def __init__(self, matrix: np.ndarray, **kwargs: Any):
        if "symmetric" in kwargs:
            kwargs.pop("symmetric")
        if "matvec" in kwargs:
            kwargs.pop("matvec")
        if "dtype" in kwargs:
            kwargs.pop("dtype")

        if not hasattr(matrix, "shape"):
            matrix = np.asanyarray(matrix)

        if matrix.ndim != 2:
            msg = "matrix must be 2-d (shape can be [M, N], [M, 1] or [1, N])"
            raise ValueError(msg)

        matvec = matrix.dot
        iscomplex = np.iscomplexobj(matrix)

        if matrix.shape[0] == matrix.shape[1]:
            symmetric = np.all(matrix == matrix.conj().T)
        else:
            symmetric = False

        if not symmetric:
            rmatvec = matrix.conj().T.dot if iscomplex else matrix.T.dot
        else:
            rmatvec = None

        super(MatrixLinearOperator, self).__init__(
            matrix.shape[1],
            matrix.shape[0],
            symmetric=symmetric,
            matvec=matvec,
            rmatvec=rmatvec,
            dtype=matrix.dtype,
            **kwargs,
        )


class ZeroOperator(LinearOperator):
    """A linear operator for a zero matrix of shape `(nargout, nargin)`

    Parameters
    ----------
    nargin : int
        _description_
    nargout : int
        _description_
    **kwargs: Any
        _description_
    """

    def __init__(self, nargin: int, nargout: int, **kwargs: Any):
        if "matvec" in kwargs:
            kwargs.pop("matvec")
        if "rmatvec" in kwargs:
            kwargs.pop("rmatvec")

        def matvec(x):
            if x.shape != (nargin,):
                msg = "Input has shape " + str(x.shape)
                msg += " instead of (%d,)" % self.nargin
                raise ValueError(msg)
            return np.zeros(nargout)

        def rmatvec(x):
            if x.shape != (nargout,):
                msg = "Input has shape " + str(x.shape)
                msg += " instead of (%d,)" % self.nargout
                raise ValueError(msg)
            return np.zeros(nargin)

        super(ZeroOperator, self).__init__(
            nargin, nargout, matvec=matvec, rmatvec=rmatvec, **kwargs
        )


class InverseLO(LinearOperator):
    r"""
    Construct the inverse operator of a matrix `A`, as a linear operator.

    Parameters
    ----------
    A : _type_
        _description_
    method : _type_, optional
        _description_, by default None
    preconditioner : _type_, optional
        _description_, by default None

    """

    def __init__(self, A, method=None, preconditioner=None):
        super(InverseLO, self).__init__(
            nargin=A.shape[0], nargout=A.shape[1], matvec=self.mult, symmetric=True
        )
        self.A = A
        self.__method = method
        self.__preconditioner = preconditioner
        self.__converged = None

    def mult(self, x):
        r"""
        It returns  :math:`y=A^{-1}x` by solving the linear system :math:`Ay=x`
        with a certain :mod:`scipy` routine (e.g. :func:`scipy.sparse.linalg.cg`)
        defined above as ``method``.
        """

        y, info = self.method(self.A, x, M=self.preconditioner)
        self.isconverged(info)
        return y

    def isconverged(self, info):
        r"""
        It returns a Boolean value  depending on the
        exit status of the solver.

        **Parameters**

        - ``info`` : {int}
            output of the solver method (usually :func:`scipy.sparse.cg`).
        """
        self.__converged = info
        if info == 0:
            return True
        else:
            return False

    @property
    def method(self):
        r"""
        The method to compute the inverse of A. \
        It can be any :mod:`scipy.sparse.linalg` solver, namely :func:`scipy.sparse.linalg.cg`,
        :func:`scipy.sparse.linalg.bicg`, etc.

        """
        return self.__method

    @property
    def converged(self):
        r"""
        provides convergence information:

        - 0 : successful exit;
        - >0 : convergence to tolerance not achieved, number of iterations;
        - <0 : illegal input or breakdown.

        """
        return self.__converged

    @property
    def preconditioner(self):
        """
        Preconditioner for the solver.
        """
        return self.__preconditioner


def ReducedLinearOperator(op, row_indices, col_indices):
    """
    Implements reduction of a linear operator (non symmetrical).

    Reduces a linear operator by limiting its input to `col_indices` and its
    output to `row_indices`.

    """

    nargin, nargout = len(col_indices), len(row_indices)
    m, n = op.shape  # Shape of non-reduced operator.

    def matvec(x):
        z = np.zeros(n, dtype=x.dtype)
        z[col_indices] = x[:]
        y = op * z
        return y[row_indices]

    def rmatvec(x):
        z = np.zeros(m, dtype=x.dtype)
        z[row_indices] = x[:]
        y = op.H * z
        return y[col_indices]

    return LinearOperator(
        nargin, nargout, matvec=matvec, symmetric=False, rmatvec=rmatvec
    )


def SymmetricallyReducedLinearOperator(op, indices):
    """
    Implements reduction of a linear operator (symmetrical).

    Reduces a linear operator symmetrically by reducing boths its input and
    output to `indices`.

    """

    nargin = len(indices)
    m, n = op.shape  # Shape of non-reduced operator.

    def matvec(x):
        z = np.zeros(n, dtype=x.dtype)
        z[indices] = x[:]
        y = op * z
        return y[indices]

    def rmatvec(x):
        z = np.zeros(m, dtype=x.dtype)
        z[indices] = x[:]
        y = op * z
        return y[indices]

    return LinearOperator(
        nargin, nargin, matvec=matvec, symmetric=op.symmetric, rmatvec=rmatvec
    )


def aslinearoperator(A):
    """Returns A as a LinearOperator.

    'A' may be any of the following types:
    - linop.LinearOperator
    - scipy.LinearOperator
    - ndarray
    - matrix
    - sparse matrix (e.g. csr_matrix, lil_matrix, etc.)
    - any object with .shape and .matvec attributes

    See the `LinearOperator` documentation for additonal information.
    """
    if isinstance(A, LinearOperator):
        return A

    try:
        import numpy as np

        if isinstance(A, np.ndarray) or isinstance(A, np.matrix):
            return MatrixLinearOperator(A)
    except ImportError:
        pass

    try:
        import scipy.sparse as ssp

        if ssp.isspmatrix(A):
            return MatrixLinearOperator(A)
    except ImportError:
        pass

    if hasattr(A, "shape"):
        nargout, nargin = A.shape
        matvec = None
        rmatvec = None
        dtype = None
        symmetric = False
        if hasattr(A, "matvec"):
            matvec = A.matvec
            if hasattr(A, "rmatvec"):
                rmatvec = A.rmatvec
            elif hasattr(A, "matvec_transp"):
                rmatvec = A.matvec_transp
            if hasattr(A, "dtype"):
                dtype = A.dtype
            if hasattr(A, "symmetric"):
                symmetric = A.symmetric
        elif hasattr(A, "__mul__"):

            def matvec(x):
                return A * x

            if hasattr(A, "__rmul__"):

                def rmatvec(x):
                    return x * A

            if hasattr(A, "dtype"):
                dtype = A.dtype
            try:
                symmetric = A.isSymmetric()
            except Exception:
                symmetric = False
        return LinearOperator(
            nargin,
            nargout,
            symmetric=symmetric,
            matvec=matvec,
            rmatvec=rmatvec,
            dtype=dtype,
        )
    else:
        raise TypeError("unsupported object type")


# some shorter aliases
MatrixOperator = MatrixLinearOperator
aslinop = aslinearoperator
