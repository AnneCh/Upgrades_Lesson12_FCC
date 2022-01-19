from scripts.helpful_scripts import get_account, encode_function_data
from brownie import network, Box, ProxyAdmin, TransparentUpgradeableProxy


# this is our implementation contract, Box.sol
# now we have to hook up our implementation contract to a proxy
# 1) give it a proxy admin (optional but if we do, it's recommended to use some type
# of default protocol)
# let's set up the Box contract as the proxy admin

# proxy contracts do not have a constructor function
# instead, we can use initializers; we could trigger the store function

# need to encode to bytes before sending to smart contract
# this is the function we call ^ when we want to create a new transparent upgradable proxy
def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy({"from": account})
    print(box.retrieve())

    proxy_admin = ProxyAdmin.deploy({"from": account})

    initializer = box.store, 1
    box_encoded_initializer_function = encode_function_data()

    proxy = TransparentUpgradeableProxy.deploy(
        box.address, proxy_admin.adress, box_encoded_initializer_function
    )
