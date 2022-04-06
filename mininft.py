import os
import sys

import click
import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

_NODE_URL = os.environ.get('NODEURL', 'http://localhost:8545')
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
]


def Hide(x):
    if len(x) > 6:
        return x[:3] + ' ... ' + x[-3:]
    return '*****'


to_hex = lambda src: '0x' + (''.join('%02x' % x for x in src))


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.0.3')
def mininft():
    pass


@mininft.command()
@click.argument('destination')
@click.argument('tokenid')
@click.option('--token', default=_TOKEN, help='Nft token address')
@click.option('--private_key', default=PRIVATE_KEY,
              help='User account private key (or env. var PRIVATE_KEY)')
@click.option('--node_url', default=_NODE_URL,
              help='Node url (defaults to env.var NODE_URL)')
@click.option('--poa', is_flag=True, help='force use POA network middleware')
def send(destination, tokenid, token, private_key, node_url, poa):
    click.echo("Node: %r" % node_url)
    click.echo("Token: %r" % token)

    if private_key is None:
        print('Private key is required. Please specify in arguments or env.',
              file=sys.stderr)
        exit(-1)
    click.echo("Private key: %r" % (Hide(private_key)))

    if not poa:
        w3 = Web3(Web3.HTTPProvider(node_url, request_kwargs={'timeout': 60}))
        poa = w3.eth.chain_id in POA_NETS
    if poa:
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract_instance = w3.eth.contract(address=token, abi=ABI_712)
    acc = w3.eth.account.from_key(private_key)

    click.echo("Account: %r" % acc.address)
    try:
        tx_hash = contract_instance.functions.safeTransferFrom(acc.address,
                                                               destination,
                                                               int(tokenid)
                                                               ).transact(
                {'from': acc.address})
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
