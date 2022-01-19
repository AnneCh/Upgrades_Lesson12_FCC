from scripts.helpful_scripts import get_account, encode_function_data
from brownie import Box, ProxyAdmin, TransparentUpgradeableProxy, Contract


def test_proxy_delegates_calls():
    # make sure we can delegate calls to our contract
    account = get_account()
    # call the deploy() on our contract
    box = Box.deploy({"from": account})
    # deploy the ProxyAdmin needed to create a proxy contract to hook to our Box contract
    proxy_admin = ProxyAdmin.deploy(
        {"from": account},
    )
    # then we encode the data(initializer function) to bytes
    box_encoded_initializer_function = encode_function_data()
    # then we deploy TransparentUpgreadableProxy to create the proxy
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
    )
    # we link the Box's contract abi to the proxy contract, delegating the proxy's received
    # calls from user to the Box's contract
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)

    # now we will test to see if the function returns 0
    # then call the store function and test once again to see if the results
    # equals the paramenter passed through the store()
    assert proxy_box.retrieve() == 0
    proxy_box.store(1, {"from": account})
    assert proxy_box.retrieve() == 1
    # now we run brownie test => successfull

    # now let's create another test file to test the upgrade
