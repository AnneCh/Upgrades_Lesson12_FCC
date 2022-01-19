from brownie import network, config, accounts
import eth_utils

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache-local", "ganache"]


def get_account(number=None):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if number:
        return accounts[number]
    if network.show_active() in config["networks"]:
        account = accounts.add(config["wallets"]["from_key"])
        return account
    return None


# ex, encode_function_data(initializer=box.store, 2) will trigger Box.sol to store 2
# as the uint that is value
def encode_function_data(initializer=None, *args):
    # there will be an issue if the length of arguments is 0:
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    return initializer.encode_input(*args)
