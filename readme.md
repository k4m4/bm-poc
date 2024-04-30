# `BM_{BLS,SB}`

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
