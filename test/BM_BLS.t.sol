// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "forge-std/Test.sol";
import {BM_BLS} from "../src/BM_BLS.sol";
import {BLS} from "../src/utils/BLS.sol";

contract BM_BLSTest is Test {
    BLS public bls;
    BM_BLS public bm_bls;

    function setUp() public {
        bls = new BLS();
        bm_bls = new BM_BLS(bls);
    }

    struct SignatureFixture {
        uint256[] apk;
        uint256[] messages;
        uint256[][] signatures;
    }

    struct SignatureHmFixture {
        uint256[] apk;
        uint256[][] messageHashes;
        uint256[][] signatures;
    }

    function _testVerifyAggrFixture(SignatureFixture memory sf) internal {
        uint256[4] memory apk = [sf.apk[0], sf.apk[1], sf.apk[2], sf.apk[3]];

        uint256[2][] memory signatures = new uint256[2][](sf.signatures.length);
        for (uint256 i = 0; i < sf.signatures.length; i++) {
            signatures[i] = [sf.signatures[i][0], sf.signatures[i][1]];
        }

        assertTrue(bm_bls.verifyAggr(
            apk,
            sf.messages,
            signatures
        ));
    }

    function testVerifyAggr() public {
        string memory path = "py/data/input_aggr.json";
        string memory json = vm.readFile(path);
        SignatureFixture memory sf = abi.decode(vm.parseJson(json), (SignatureFixture));
        _testVerifyAggrFixture(sf);
    }

    function _testVerifyAggrHmFixture(SignatureHmFixture memory sf) internal {
        uint256[4] memory apk = [sf.apk[0], sf.apk[1], sf.apk[2], sf.apk[3]];

        uint256[2][] memory signatures = new uint256[2][](sf.signatures.length);
        for (uint256 i = 0; i < sf.signatures.length; i++) {
            signatures[i] = [sf.signatures[i][0], sf.signatures[i][1]];
        }

        uint256[2][] memory messageHashes = new uint256[2][](sf.messageHashes.length);
        for (uint256 i = 0; i < sf.messageHashes.length; i++) {
            messageHashes[i] = [sf.messageHashes[i][0], sf.messageHashes[i][1]];
        }

        assertTrue(bm_bls.verifyAggrHm(
            apk,
            messageHashes,
            signatures
        ));
    }

    function testVerifyAggrHm() public {
        string memory path = "py/data/input_aggr_hm.json";
        string memory json = vm.readFile(path);
        SignatureHmFixture memory sf = abi.decode(vm.parseJson(json), (SignatureHmFixture));
        _testVerifyAggrHmFixture(sf);
    }

    function testVerify() public {
        uint256[2] memory signature = [
            12099452429872967987634519446390896416640783663211103224510701214821200133031,
            3420189633381407834375402388798786420867278826105219661196695221102155212665
        ];

        uint256 m = 1337;

        uint256[4] memory apk = [
            1762823541261255583852588287246821943711074602478239424925892892188174075550,
            12101232060753965759744661756265291416779178726820745120170203257891120604243,
            18253644835102415928318683038816585553574861004181078377709300597603336517648,
            16745628324223498065413617918817223827456355266743326679895626713079800565647
        ];

        assertTrue(bm_bls.verify(apk, m, signature));
        assertTrue(bm_bls.usedCredentials(sha256(abi.encode(signature))));
    }
}
