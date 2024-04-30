// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "forge-std/Test.sol";
import {BM_SB} from "../src/BM_SB.sol";
import {BLS} from "../src/utils/BLS.sol";

contract BM_SBTest is Test {
    BLS public bls;
    BM_SB public bm_sb;

    function setUp() public {
        bls = new BLS();
        bm_sb = new BM_SB(bls);
    }

    struct SignatureFixture {
        uint256[] R_bar;
        uint256 m;
        uint256[][] pks;
        uint256 y_bar;
        uint256 z_bar;
    }

    function _testVerifyFixture(SignatureFixture memory sf) internal {
        uint256[2][] memory pks = new uint256[2][](sf.pks.length);
        for (uint256 i = 0; i < sf.pks.length; i++) {
            pks[i] = [sf.pks[i][0], sf.pks[i][1]];
        }

        uint256[2] memory R_bar = [sf.R_bar[0], sf.R_bar[1]];

        assertTrue(bm_sb.verify(
            pks,
            sf.m,
            R_bar,
            sf.y_bar,
            sf.z_bar
        ));
    }

    function testVerify() public {
        string memory path = "py/data/input.json";
        string memory json = vm.readFile(path);
        SignatureFixture memory sf = abi.decode(vm.parseJson(json), (SignatureFixture));
        _testVerifyFixture(sf);
    }
}
