# `BM_{BLS,SB}` PoC

> Implementation of single-use, anonymous tokens with decentralized issuance and public verifiability

## Testing

To run the smart contract tests (requires [Foundry](https://book.getfoundry.sh/getting-started/installation)), execute:

```sh
forge test
```

To run the Python tests, execute:

```sh
cd py
poetry shell
maturin develop --release
python -m unittest *.py
```
