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

from .misc import TypeChangeWarning, LowerTypeCastWarning, filter_warnings, ShapeError

from .linop import (
    BaseLinearOperator,
    LinearOperator,
    IdentityOperator,
    DiagonalOperator,
    MatrixLinearOperator,
    ZeroOperator,
    InverseLO,
    ReducedLinearOperator,
    SymmetricallyReducedLinearOperator,
    aslinearoperator,
    null_log,
)

from .blkop import (
    BlockLinearOperator,
    BlockDiagonalLinearOperator,
    BlockPreconditioner,
    BlockDiagonalPreconditioner,
    BlockHorizontalLinearOperator,
    BlockVerticalLinearOperator,
)

from .noise_ops import (
    NoiseCovLinearOperator,
    InvNoiseCovLinearOperator,
    BaseBlockDiagNoiseCovLinearOperator,
    BaseBlockDiagInvNoiseCovLinearOperator,
)

__all__ = [
    # misc.py
    "TypeChangeWarning",
    "LowerTypeCastWarning",
    "filter_warnings",
    "ShapeError",
    # linop.py
    "BaseLinearOperator",
    "LinearOperator",
    "IdentityOperator",
    "DiagonalOperator",
    "MatrixLinearOperator",
    "ZeroOperator",
    "InverseLO",
    "ReducedLinearOperator",
    "SymmetricallyReducedLinearOperator",
    "aslinearoperator",
    "null_log",
    # blkop.py
    "BlockLinearOperator",
    "BlockDiagonalLinearOperator",
    "BlockPreconditioner",
    "BlockDiagonalPreconditioner",
    "BlockHorizontalLinearOperator",
    "BlockVerticalLinearOperator",
    # noise_ops.py
    "NoiseCovLinearOperator",
    "InvNoiseCovLinearOperator",
    "BaseBlockDiagNoiseCovLinearOperator",
    "BaseBlockDiagInvNoiseCovLinearOperator",
]
