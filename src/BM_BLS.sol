// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import {IBLS} from "./interfaces/IBLS.sol";
import {BN254} from "./libs/BN254.sol";

contract BM_BLS {
    bytes32 public constant DOMAIN = sha256("DOMAIN_BM_BLS");

    IBLS public immutable bls;

    mapping(bytes32 => bool) public usedCredentials;

    constructor(IBLS newBLS) {
        bls = newBLS;
    }

    function verify(
        uint256[4] calldata apk,
        uint256 m,
        uint256[2] calldata signature
    )
        external
        returns (bool)
    {
        bytes32 credentialHash = sha256(abi.encode(signature));
        require(!usedCredentials[credentialHash], "Credential already used");

        usedCredentials[credentialHash] = true;

        uint256[2] memory hm = bls.hashToPoint(DOMAIN, abi.encode(m));

        (bool checkSuccess, bool callSuccess) = bls.verifySingle(signature, apk, hm);
        return callSuccess && checkSuccess;
    }

    function verifyAggr(
        uint256[4] calldata apk,
        uint256[] calldata messages,
        uint256[2][] calldata signatures
    )
        external
        returns (bool)
    {
        require(signatures.length > 0 && signatures.length == messages.length);
        for (uint256 i = 0; i < signatures.length; i++) {
            bytes32 credentialHash = sha256(abi.encode(signatures[i]));
            require(!usedCredentials[credentialHash], "Credential already used");
            usedCredentials[credentialHash] = true;
        }

        uint256[2] memory signature = signatures[0];
        for (uint256 i = 1; i < signatures.length; i++) {
            signature = BN254.ecAdd(signature, signatures[i]);
        }

        uint256[2] memory hash = bls.hashToPoint(DOMAIN, abi.encode(messages[0]));
        for (uint256 i = 1; i < messages.length; i++) {
            hash = BN254.ecAdd(
                hash,
                bls.hashToPoint(DOMAIN, abi.encode(messages[i]))
            );
        }

        (bool checkSuccess, bool callSuccess) = bls.verifySingle(signature, apk, hash);
        return callSuccess && checkSuccess;
    }

    function verifyAggrHm(
        uint256[4] calldata apk,
        uint256[2][] calldata messageHashes,
        uint256[2][] calldata signatures
    )
        external
        returns (bool)
    {
        require(signatures.length > 0 && signatures.length == messageHashes.length);
        for (uint256 i = 0; i < signatures.length; i++) {
            bytes32 credentialHash = sha256(abi.encode(signatures[i]));
            require(!usedCredentials[credentialHash], "Credential already used");
            usedCredentials[credentialHash] = true;
        }

        uint256[2] memory signature = signatures[0];
        for (uint256 i = 1; i < signatures.length; i++) {
            signature = BN254.ecAdd(signature, signatures[i]);
        }

        uint256[2] memory hash = messageHashes[0];
        for (uint256 i = 1; i < messageHashes.length; i++) {
            hash = BN254.ecAdd(
                hash,
                messageHashes[i]
            );
        }

        (bool checkSuccess, bool callSuccess) = bls.verifySingle(signature, apk, hash);
        return callSuccess && checkSuccess;
    }
}
