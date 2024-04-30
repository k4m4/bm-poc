// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "forge-std/Test.sol";
import {BN254} from "../src/libs/BN254.sol";

contract BN254Test is Test {
    uint256[2] public G1 = [uint256(1), uint256(2)];

    function testEcAdd() public {
        uint256[2] memory retP = BN254.ecAdd(G1, G1);
        assertEq(retP[0], 1368015179489954701390400359078579693043519447331113978918064868415326638035);
        assertEq(retP[1], 9918110051302171585080402603319702774565515993150576347155970296011118125764);
    }

    function testEcMul() public {
        uint256[2] memory retP = BN254.ecMul(G1, 1);
        assertEq(retP[0], G1[0]);
        assertEq(retP[1], G1[1]);
    }
}
