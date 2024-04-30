// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

library BN254 {
    function ecAdd(uint256[2] calldata p0, uint256[2] calldata p1)
        external
        view
        returns (uint256[2] memory retP)
    {
        uint256[4] memory bnAddInput = [p0[0], p0[1], p1[0], p1[1]];
        bool success;
        assembly {
            success := staticcall(sub(gas(), 2000), 0x06, bnAddInput, 128, retP, 64)
            switch success
            case 0 { invalid() }
        }
        require(success, "BN254: bn add call failed");
    }

    function ecMul(uint256[2] calldata p, uint256 s)
        external
        view
        returns (uint256[2] memory retP)
    {
        uint256[3] memory bnMulInput = [p[0], p[1], s];
        bool success;
        assembly {
            success := staticcall(sub(gas(), 2000), 0x07, bnMulInput, 128, retP, 64)
            switch success
            case 0 { invalid() }
        }
        require(success, "BN254: bn mul call failed");
    }
}
