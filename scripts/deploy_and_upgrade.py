from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    network,
    Box,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    BoxV2,
)


# this is our implementation contract, Box.sol
# now we have to hook up our implementation contract to a proxy
# 1) give it a proxy admin (optional but if we do, it's recommended to use some type
# of default protocol)
# let's set up a proxy admin instead of being us

# proxy contracts do not have a constructor function
# instead, we can use initializers; we could trigger the store function

# need to encode to bytes before sending to smart contract
# this is the function we call when we want to create a new transparent upgradable proxy
def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy({"from": account})
    print(box.retrieve())

    proxy_admin = ProxyAdmin.deploy({"from": account})

    initializer = box.store, 1
    box_encoded_initializer_function = encode_function_data()
    # in this example, we are telling it not to use an initializer, by leaving the function without arguments

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
    )
    print(f"Proxy deployed to {proxy}, you can now upgrade to V2")
    # now we can call functions on the proxy's address by attaching the Box's ABI to the proxy's address
    # if it weren't a proxy, attaching a contract's ABI that has functions that the address
    # it's attached to doesn't have, it would error out
    # but the proxy contract delegates all of its calls to the Box contract
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)

    # now we can call the store function and setting 1 as an argument, then retrieve 1
    proxy_box.store(1, {"from": account})
    print(proxy_box.retrieve())
    # sucessfully deployed the proxy contract, and called a Box's function thru the proxy,
    # saving the retrieved data in the proxy

    # NOW, let's deploy a V2 implementation contract
    box_v2 = BoxV2.deploy({"from": account})

    # now we gotta call the upgradeTo function from TransparentUpgradeableProxy.sol
    # we will wrap it up onto its own upgrade function : helpfulscripts
    upgrade_transaction = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    upgrade_transaction.wait(1)
    print("Proxy has been upgraded to V2!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    # now we can try to call the increment function present on V2 and not on V1
    proxy_box.increment({"from": account})
    print(proxy_box.retrieve())
    # worked out correctly, printed 2


# Now it's time for testing!!
