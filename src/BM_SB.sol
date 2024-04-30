// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import {IBLS} from "./interfaces/IBLS.sol";
import {BN254} from "./libs/BN254.sol";

contract BM_SB {
    bytes32 public constant DOMAIN = sha256("DOMAIN_BM_SB");
    bytes public constant DOMAIN_ENCODED = abi.encode(DOMAIN);

    uint256 private constant CURVE_ORDER = 21888242871839275222246405745257275088548364400416034343698204186575808495617;

    IBLS public immutable bls;

    mapping(bytes32 => bool) public usedCredentials;

    constructor(IBLS newBLS) {
        bls = newBLS;
    }

    uint256[2] g = [1, 2];
    uint256[2] h = [3353031288059533942658390886683067124040920775575537747144343083137631628272, 19321533766552368860946552437480515441416830039777911637913418824951667761761];

    function _encodePoints(uint256[2][] calldata points) internal pure returns (bytes memory encodedPoints) {
        for (uint256 i = 0; i < points.length; i++) {
            encodedPoints = abi.encodePacked(encodedPoints, abi.encode(points[i]));
        }
    }

    function verify(
        uint256[2][] calldata pks,
        uint256 m,
        uint256[2] calldata R_bar,
        uint256 y_bar,
        uint256 z_bar
    )
        external
        returns (bool)
    {
        bytes32 credentialHash = sha256(abi.encode(R_bar, y_bar, z_bar));
        require(!usedCredentials[credentialHash], "Credential already used");

        usedCredentials[credentialHash] = true;

        bytes memory encoded_pks = _encodePoints(pks);
        bytes memory encoded_m = abi.encode(m);
        bytes memory encoded_R_bar = abi.encode(R_bar);

        uint256[] memory c_i_bar = new uint256[](pks.length);
        for (uint256 i = 0; i < pks.length; i++) {
            c_i_bar[i] = uint256(sha256(abi.encodePacked(
                DOMAIN_ENCODED,
                encoded_pks,
                abi.encode(pks[i]),
                encoded_m,
                encoded_R_bar
            )));
        }

        uint256 y_bar_cubed = mulmod(
            mulmod(y_bar, y_bar, CURVE_ORDER),
            y_bar,
            CURVE_ORDER
        );

        uint256[2] memory sum = BN254.ecMul(
            pks[0],
            addmod(c_i_bar[0], y_bar_cubed, CURVE_ORDER)
        );

        for (uint256 i = 1; i < pks.length; i++) {
            sum = BN254.ecAdd(
                sum,
                BN254.ecMul(
                    pks[i],
                    addmod(c_i_bar[i], y_bar_cubed, CURVE_ORDER)
                )
            );
        }

        uint256[2] memory LHS = BN254.ecAdd(
            R_bar,
            sum
        );

        uint256[2] memory RHS = BN254.ecAdd(
            BN254.ecMul(g, z_bar),
            BN254.ecMul(h, y_bar)
        );

        return y_bar != 0 && RHS[0] == RHS[0] && RHS[1] == LHS[1];
    }
}
