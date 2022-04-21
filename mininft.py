import os
import re
import sys

import click
import web3
from eth_account.datastructures import SignedTransaction
from web3 import Web3
from web3.middleware import geth_poa_middleware


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

_NODE_URL = os.environ.get('NODEURL',
                           os.environ.get('NODE_URL',
                                          'http://localhost:8545'))
_TOKEN = Web3.toChecksumAddress(os.environ.get('NFT',
                                               os.environ.get('TOKEN',
                                                              '0x3d7Eec9C41c7A99489fD17e6B087f9C827b16d3F')))
PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
POA_NETS = {97, 56, 4}
ABI_712 = [
    {
        "constant": False,
        "inputs": [
            {
                "internalType": "address",
                "name": "from",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
            }
        ],
        "name": "safeTransferFrom",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {
                "internalType": "address",
                "name": "from",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
            },
        ],
        "name": "transferFrom",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
            },
        ],
        "name": "transfer",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
]


class Terminate(Exception):
    pass


def hide(x):
    if len(x) > 6:
        return x[:3] + ' ... ' + x[-3:]
    return '*****'


to_hex = lambda src: '0x' + (''.join('%02x' % x for x in src))


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.0.6')
def mininft():
    # this is a placeholder for common configurations for different actions..
    # currently there's only one..
    pass


@mininft.command()
@click.argument('destination')
@click.argument('tokenid')
@click.option('--token', default=_TOKEN, help='Nft token address')
@click.option('--private_key', default=PRIVATE_KEY,
              help='User account private key (or env. var PRIVATE_KEY)')
@click.option('--node_url', default=_NODE_URL,
              help='Node url (defaults to env.var NODE_URL)')
@click.option('--gas_price',
              help='gas price (eg:`10gwei`) default reads from network')
@click.option('--poa', is_flag=True, help='force use POA network middleware')
def send(destination, tokenid, token, private_key, node_url, poa,
         gas_price=None):
    click.echo("Node: %r" % node_url)
    click.echo("Token: %r" % token)

    if private_key is None:
        print('Private key is required. Please specify in arguments or env.',
              file=sys.stderr)
        exit(-1)
    click.echo("Private key: %r" % (hide(private_key)))

    chain_id = None
    if not poa:
        w3 = Web3(Web3.HTTPProvider(node_url, request_kwargs={'timeout': 60}))
        chain_id = w3.eth.chain_id
        poa = chain_id in POA_NETS
    if poa:
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract_instance = w3.eth.contract(address=token, abi=ABI_712)

    acc = w3.eth.account.from_key(private_key)
    click.echo("Account: %r" % acc.address)
    balance = w3.eth.getBalance(acc.address)
    click.echo("Balance for %r: %d" % (acc.address, balance))

    # gas price handling
    if gas_price is None:
        # take from network
        _gas_price = w3.eth.gasPrice
    else:
        magnitud_unidad = re.compile("^([0-9]*)([a-zA-Z]*)$")
        m = magnitud_unidad.match(gas_price)
        if m:
            g = m.groups()
            _gas_price = w3.toWei(g[0], g[1])
        else:
            raise Terminate("Failed to extract gas price from: %r" % gas_price)
    click.echo("Gas price: %d" % _gas_price)

    try:
        if chain_id is None:
            chain_id = w3.eth.chain_id

        tx = contract_instance.functions.transferFrom(acc.address, destination,
                                            int(tokenid) ).buildTransaction({
            'from': acc.address,
            'chainId': chain_id,
            'gasPrice': _gas_price,
            'nonce': w3.eth.getTransactionCount(acc.address),
        })
        signed_txn: SignedTransaction = w3.eth.account.sign_transaction(tx,
                                                                    private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        click.echo("tx hash: %s" % to_hex(tx_hash))
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        # click.echo("receipt: %s" % tx_receipt)
        msgs = {True: 'Tx success.', False: 'Tx reverted'}
        click.echo(msgs[tx_receipt['status'] == 1])

    except web3.exceptions.ContractLogicError as error:
        click.echo("can't send token. No Tx")
        click.echo("error msg: %s" % error.args[0])
        exit(-1)


if __name__ == '__main__':
    mininft()
