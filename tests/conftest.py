import pytest


@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.12.3/tests-pytest-intro.html#isolation-fixtures
    pass


@pytest.fixture(scope="module")
def frontrunner(accounts):
    return accounts[4]


@pytest.fixture(scope="module")
def kidnapper(accounts):
    return accounts[3]


@pytest.fixture(scope="module")
def friends(accounts):
    return accounts[2]


@pytest.fixture(scope="module")
def victim(accounts):
    return accounts[1]


@pytest.fixture(scope="module")
def insurance(KidnapInsurance, victim, friends):
    return KidnapInsurance.deploy(friends, {'from': victim, 'value': "10 ether"})


@pytest.fixture(scope="module")
def password():
    return "s3cr3tphras3"

