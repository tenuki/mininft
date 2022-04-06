# Mininft: transfer your nft

## Execution

* `mininft <destination> <tokenid>`

```shell
Usage: mininft send [OPTIONS] DESTINATION TOKENID

Options:
  --token TEXT        Nft token address
  --private_key TEXT  User account private key (or env. var PRIVATE_KEY)
  --node_url TEXT     Node url (defaults to env.var NODE_URL)
  --poa               force use POA network middleware
  -h, --help          Show this message and exit.
```



Example:

`set PRIVATE_KEY=..`
`mininft send --token 0x3d7Eec9C41c7A99489fD17e6B087f9C827b16d3F  0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1 1`

Output:

```
Node: 'http://localhost:8545'
Token: '0x3d7Eec9C41c7A99489fD17e6B087f9C827b16d3F'
Private key: '4f3 ... b1d'
Account: '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'
tx hash: 0xf2b422a57363f8cc63a02047f344160f02caf585ee183724d0e81db7d6be0b5d
Tx success.
```
