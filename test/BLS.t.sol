// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "forge-std/Test.sol";
import "forge-std/console.sol";
import {BLS} from "../src/utils/BLS.sol";

contract BLSTest is Test {
    BLS public bls;

    bytes32 public constant DOMAIN = sha256("DOMAIN_BLS");

    function setUp() public {
        bls = new BLS();
    }

    function testMapToPoint() public {
        uint256[2] memory p = bls.mapToPoint(1337);
        assertEq(p[0], 8530237650951294995081296786571254989712779769533722451509137284836421790461);
        assertEq(p[1], 9470826407334717825665908825387707341464461595687922993989697758038342982627);
    }

    function testMapToPointZero() public {
        uint256[2] memory p = bls.mapToPoint(0);
        assertEq(p[0], 2203960485148121921418603742825762020974279258880205651966);
        assertEq(p[1], 2);
    }

    function testHashToField() public {
        uint256[2] memory p = bls.hashToField(DOMAIN, "1337");
        assertEq(p[0], 9318611549105079201796255165034801330003143592412227428031940328845719820421);
        assertEq(p[1], 17481204086648883119547741059325852324286758138419390304093670150793071400260);
    }

    function testHashToPoint() public {
        uint256[2] memory p = bls.hashToPoint(DOMAIN, "1337");
        assertEq(p[0], 10500695014734979431623563580570724763115533399989856133560600372558107769431);
        assertEq(p[1], 12356362133861447212720988676687243749348329265811660859066767007757826012392);
    }

    function testVerifyAggregatedSignatureWithOneMessage() public {
        uint256 n = 1;
        uint256[2] memory aggSignature = [
            0x150a9d2def9b5c5fa811e1d6982442563b9dde2b921e17bf0a1086700729baf4,
            0x103ebf2582b16f8dcfcff58ed861cf83798effd93c6b85fe7b64f6ba86fbdc5a
        ];
        uint256[4][] memory pubkeys = new uint256[4][](n);
        uint256[4] memory pubkey = [
            0x2ee8f12ffb91094c4c7dcb86013fc24c63afe2281508f5cee3d5e398a446da6f,
            0x16323f4b31c74da853938c963ed591a622df693c1b38acd4afeb3b433415f617,
            0x082dbb9e240107e59fc0baeda6fcc21e0f3ae64f529f90920b3f0bc60d41c43d,
            0x12a1bd1fb0e2e6b96a25c751e70878239ada46d5d5bc3848ab275335830e6876
        ];
        pubkeys[0] = pubkey;
        uint256[2][] memory messages = new uint256[2][](n);
        uint256[2] memory message = [
            0x036bf1f7994cc0e919953f0bd0b3ddcc6e73c618f2f92ff1c0a556be40ecda1c,
            0x3001dd7f091d6a799e492c1ffe43930f6da0833cece7711e1b7f28db0c2ffb33
        ];
        messages[0] = message;
        (bool res0, bool res1) = bls.verifyMultiple(aggSignature, pubkeys, messages);
        assertTrue(res0);
        assertTrue(res1);
    }

    function testVerifyAggregatedSignatureWithTwoMessages() public {
        uint256 n = 2;
        uint256[2] memory aggSignature = [
            0x126d32c5e46550a0ae8f7dabd23acbc29940bf64e8dc1f26dfc2da78d41ac341,
            0x05a3c3c6742410feab00737f080bf528c2551b59a53bf3e3bea77aef4d1b8120
        ];
        uint256[4][] memory pubkeys = new uint256[4][](n);
        uint256[4] memory pubkey1 = [
            0x02faf5a06e584955af30829059c7ca5a90fc48dfdee5886b37d62c6fadd59a10,
            0x18f33d2577c04a90994a2306e67e55c7715f4593572f29f326b3cb8e01cbe9b5,
            0x077e62c4c3cf4eef364e13d62309a1c169ee321587c60c100a7482e8aa433146,
            0x1c4f3c2590a93595757a72571350e7494b9df56b8dba03d107d699ed22eb77f0
        ];
        uint256[4] memory pubkey2 = [
            0x1defee2c2ae4df09bf3826ac0ee75a0dc6735a9c62e7a9206417420287e62970,
            0x2db3aae0ce78ccaec39f91abfee9ea41d740f694e490e1ceb055ca412d682e44,
            0x1b36d3a11db64be510aa7d1df4c8eeb3f41711cd87da54fe4946ec4be6e75bdc,
            0x13f53d9746f0edadf8d1a5a8861a6d4be4b1ae5d813c8d0e2fcb7cb34dfbf501
        ];
        pubkeys[0] = pubkey1;
        pubkeys[1] = pubkey2;
        uint256[2][] memory messages = new uint256[2][](n);
        uint256[2] memory message1 = [
            0x0d3b8522cee4d74448607b503a0ad0dad402c6b8845b68f505f2397f20762ae9,
            0x187fd6a338c7d3affbfd00ae031be5fedd64f70057d207ee6ccad9a351d6f8f5
        ];
        uint256[2] memory message2 = [
            0x05100cd25a1ea408c2d6fcb050f204014bd1099599ef3fbf8e93619879880b45,
            0x0cb9c124f40572fee46b93d34b023e446538ccac9554887f28bc4cc535509de3
        ];
        messages[0] = message1;
        messages[1] = message2;
        (bool res0, bool res1) = bls.verifyMultiple(aggSignature, pubkeys, messages);
        assertTrue(res0);
        assertTrue(res1);
    }

    function testVerifyAggregatedSignatureSameMessage() public {
        uint256 n = 2;
        uint256[2] memory aggSignature = [
            0x1df2692bcb161ec252e7d6e10e357975c4a544a5b20e69c5b3321902ec403e9d,
            0x1a469e279c1ebfbccdee7c79918dda903a3c48f005b9464c0e46f2076e0960f3
        ];
        uint256[4][] memory pubkeys = new uint256[4][](n);
        uint256[4] memory pubkey1 = [
            0x0dec859e06000284f9a4383d007f0d4a663c62702deca87005b257cb87d60e24,
            0x073b93336f86c16e3a9591c27886980b29e675a06b32372c2b7851cba3a5b20d,
            0x0c8dbd4aabb346b53a016e2062c02c7f4c0cdab0fe9f0d1ab24ca585fcce3d12,
            0x2c359374ad0bb55129b6790f95cc22b5ece4a0ead11744edd740bad42a887ffe
        ];
        uint256[4] memory pubkey2 = [
            0x1cff1609ffe8803a7888cb4a401fc2bf879fe300e675c296dce455735ab90ca5,
            0x22a6d7fb5dc1ae42a805e6205cb62f3675e9050f07cbca2dd9e750ea22e0e144,
            0x289904d5aca0feff64b6860ddce1e2c2605877cf4d6d8f5f6d6f934ebec5f339,
            0x2bc82028ab5dc28b9cfe163798c70179221765f219210657d9190f93554dc502
        ];
        pubkeys[0] = pubkey1;
        pubkeys[1] = pubkey2;
        uint256[2] memory message = [
            0x0f710c3f4b8a00e58ad857a8ce1494b7ab6caa67f1e9c4c2ffbcca8eb91d7d58,
            0x1bef25a5e14b3dc699d6bf1b918910f2e0c43224cc32aaa466a947fdd7fe2146
        ];
        (bool res0, bool res1) = bls.verifyMultipleSameMsg(aggSignature, pubkeys, message);
        assertTrue(res0);
        assertTrue(res1);
    }

    function testVerifyAggregatedSignatureAggregatedPublicKey() public {
        uint256[2] memory aggSignature = [
            0x0995ab08c8b09f3ee447eef8a2b04f6bea9675c996e6c7d9f739e29821fbb9b7,
            0x2aa6249c98a7af841252a3a177156486a8566395f7f79f75228ffd9bec437e98
        ];
        uint256[4] memory aggPublicKey = [
            0x100b757cd149fa5b71652d50923748b12b0346040456efcce7784feff975f68a,
            0x13353ff9c1c313b6480653679ea774f3b79bd8e27e07ab89e2b59d8a4fbbfde6,
            0x2edbfc8dea54a82954ba29659c4809a9ea3d0c2c460128d312de78d99cafe299,
            0x238a190a0eefe58ec89f71687f4a0eaf99e16ff58af1f22ec61037fa4720be0c
        ];
        uint256[2] memory message = [
            0x1c0828fe8ebac3bfd36b767e57f1bbedbf1089230f4e256085538cb774206a0b,
            0x203b40273d1673eafeb2253e001df434aeb40bbba9e1eab0ee700e506d57b05b
        ];
        (bool res0, bool res1) = bls.verifySingle(aggSignature, aggPublicKey, message);
        assertTrue(res0);
        assertTrue(res1);
    }
}
