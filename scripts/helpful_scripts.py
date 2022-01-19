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
# Encoding the function call allows us to work with an initializer
def encode_function_data(initializer=None, *args):
    # there will be an issue if the length of arguments is 0:
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    return initializer.encode_input(*args)


def upgrade(
    account,
    proxy,
    newimplementation_address,
    proxy_admin_contract=None,
    initializer=None,
    *args
):
    # First let's see if there's already a proxy Admin contract
    # if there is one, 1) encode the function
    # 2) call the function UpgradeAndCall on the admin contract (if there's an initializer, call is necessary)
    # that function takes an address for the proxy, a new implementation address, the encode function, and an account
    transaction = None
    if proxy_admin_contract:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                newimplementation_address,
                encoded_function_call,
                {"from": account},
            )
        else:  # if there's no initializer
            transaction = proxy_admin_contract.upgrade(
                proxy.address, newimplementation_address, {"from": account}
            )
    # if there's no admin contract, check if there is an initializer:
    else:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy.upgradeToAndCall(
                newimplementation_address,
                encoded_function_call,
                {"from": account},
            )
        else:
            transaction = proxy.upgradeTo(newimplementation_address, {"from": account})
    return transaction


# now we can go call the upgrade function in deploy_and_upgrade
