# `BM_{BLS,SB}` PoC

> Proof-of-concept implementations of anonymous tokens with decentralized issuance.

## Testing

To run the smart contract tests (requires [Foundry](https://book.getfoundry.sh/getting-started/installation)), execute:

```sh
forge test
```

To run the Python tests (requires [Poetry](https://python-poetry.org/docs/)), execute:

```sh
cd py
poetry shell
poetry install
maturin develop --release
python -m unittest *.py
```

## Benchmarks

To run the smart contract gas benchmarks (requires [Foundry](https://book.getfoundry.sh/getting-started/installation) and [Poetry](https://python-poetry.org/docs/)), execute:

```sh
cd py
poetry shell
poetry install
maturin develop --release
NUM_MESSAGES=2 NUM_SIGNERS=11 python generate-fixtures.py && forge test --mc BM_BLS --gas-report
NUM_SIGNERS=11 python generate-fixtures.py && forge test --mc BM_SB --gas-report
```
