from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    network,
    Box,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    BoxV2,
)

# publish_source=True allows to see on Etherscan
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
    box = Box.deploy({"from": account}, publish_source=True)
    # Optional, deploy the ProxyAdmin and use that as the admin contract
    proxy_admin = ProxyAdmin.deploy({"from": account}, publish_source=True)

    # initializer = box.store, 1
    box_encoded_initializer_function = encode_function_data()
    # in this example, we are telling it not to use an initializer, by leaving the function without arguments

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
        publish_source=True,
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
    box_v2 = BoxV2.deploy({"from": account}, publish_source=True)

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
# worked well on rinkeby, contracts were deployed :
"""
anne@AnneSager:~/demos/upgrades$ brownie run scripts/deploy_and_upgrade.py --network rinkeby
Brownie v1.17.2 - Python development framework for Ethereum

UpgradesProject is the active project.

Running 'scripts/deploy_and_upgrade.py::main'...
Deploying to rinkeby
Transaction sent: 0x79fb880f2a3ab4c5e3b7d24212b36920369475ac87f142687eee20770acbae11
  Gas price: 1.000000029 gwei   Gas limit: 113391   Nonce: 136
  Box.constructor confirmed   Block: 10023591   Gas used: 103083 (90.91%)
  Box deployed at: 0xc286719ed89641DC0dC2E2E2F89A7807687b216C

Waiting for https://api-rinkeby.etherscan.io/api to process contract...
Verification submitted successfully. Waiting for result...
Verification pending...
Verification complete. Result: Pass - Verified
Transaction sent: 0x269eaf06f3b4f87ee45a223b9bbefb84834f5d1b6dc6ad0210229b01e388acba
  Gas price: 1.000000029 gwei   Gas limit: 534673   Nonce: 137
  ProxyAdmin.constructor confirmed   Block: 10023594   Gas used: 486067 (90.91%)
  ProxyAdmin deployed at: 0xF7f390e1c67Ef61D8305eC7ea6d3a0A0AA472C35

Waiting for https://api-rinkeby.etherscan.io/api to process contract...
Verification submitted successfully. Waiting for result...
Verification pending...
Verification pending...
Verification pending...
Verification complete. Result: Pass - Verified
Transaction sent: 0xa7676407ebb9b105a4a2a8475063cfe660c585be2624c9214b3d26257f2aab4c
  Gas price: 1.000000028 gwei   Gas limit: 1000000   Nonce: 138
  TransparentUpgradeableProxy.constructor confirmed   Block: 10023600   Gas used: 587516 (58.75%)
  TransparentUpgradeableProxy deployed at: 0x82CfbCCE1616f658e5c90e4a17Ba30D4FbABa801

Verification submitted successfully. Waiting for result...
Verification complete. Result: Already Verified
Proxy deployed to 0x82CfbCCE1616f658e5c90e4a17Ba30D4FbABa801, you can now upgrade to V2
Transaction sent: 0xe7cb765ff4b537d61aaf48015d7dbee0f88fb7346b4e0f3476c547deac91f657
  Gas price: 1.000000027 gwei   Gas limit: 57466   Nonce: 139
  Transaction confirmed   Block: 10023606   Gas used: 51909 (90.33%)

1
Transaction sent: 0x2e156e47fea4226c2a851199c826c40887ab9c6b9306e413cbcf3084f81e07fc
  Gas price: 1.000000026 gwei   Gas limit: 146012   Nonce: 140
  BoxV2.constructor confirmed   Block: 10023607   Gas used: 132739 (90.91%)
  BoxV2 deployed at: 0x26D4CCD87aB6b820Eb5D90e15d572FD6e3D710F7

Waiting for https://api-rinkeby.etherscan.io/api to process contract...
Verification submitted successfully. Waiting for result...
Verification pending...
Verification complete. Result: Already Verified
Transaction sent: 0x250e66b1604a0cf54030a1aea438a7a7fa85907c0e19df750ebf028ca1e2d029
  Gas price: 1.000000027 gwei   Gas limit: 42787   Nonce: 141
  ProxyAdmin.upgrade confirmed   Block: 10023612   Gas used: 38760 (90.59%)

  ProxyAdmin.upgrade confirmed   Block: 10023612   Gas used: 38760 (90.59%)

Proxy has been upgraded to V2!
Transaction sent: 0x16f0bf17c480dc7b7ce1d317d7ab52bdd5b46a539790b640fabf3259cff09585
  Gas price: 1.000000025 gwei   Gas limit: 38218   Nonce: 142
  Transaction confirmed   Block: 10023613   Gas used: 34682 (90.75%)

2
"""
