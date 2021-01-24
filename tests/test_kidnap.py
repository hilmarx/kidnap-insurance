from brownie import Wei, reverts


def test_rescued(committed_insurance, chain, kidnapper, password):
    ransom = Wei("10 ether")
    initial_kidnapper = kidnapper.balance()
    committed_insurance.initiateRansomWithdraw(password, ransom, {'from': kidnapper})
    chain.sleep(60 * 60 * 24 * 3 + 1000)  # 3 days and 1000 seconds
    committed_insurance.withdrawRansom({'from': kidnapper})
    assert initial_kidnapper + ransom == kidnapper.balance()


def test_abducted_rescued(committed_insurance, chain, kidnapper, password):
    ransom = Wei("10 ether")
    tx = committed_insurance.initiateRansomWithdraw(password, ransom, {'from': kidnapper})
    assert "Abducted" in tx.events
    assert tx.events["Abducted"].values() == [kidnapper, ransom]

    chain.sleep(60 * 60 * 24 * 3 + 1000)  # 3 days and 1000 seconds
    tx = committed_insurance.withdrawRansom({'from': kidnapper})
    assert "Rescued" in tx.events


def test_ransom_too_high(committed_insurance, kidnapper, password):
    ransom = Wei("100 ether")
    with reverts("Kidnapper: Not enough ransom available"):
        committed_insurance.initiateRansomWithdraw(password, ransom, {'from': kidnapper})


def test_friends_increase_deposit(committed_insurance, kidnapper, password, friends):
    ransom = Wei("100 ether")
    friends.transfer(committed_insurance, "90 ether")
    committed_insurance.initiateRansomWithdraw(password, ransom, {'from': kidnapper})
    assert committed_insurance.ransomAmount() == ransom


def test_wrong_password(committed_insurance, kidnapper):
    with reverts("Kidnapper: Invalid password or sender"):
        committed_insurance.initiateRansomWithdraw("wrong password", "1 ether", {'from': kidnapper})


def test_no_early_withdraw(committed_insurance, kidnapper, password):
    committed_insurance.initiateRansomWithdraw(password, "10 ether", {'from': kidnapper})
    with reverts("Kidnapper: Cannot withdraw yet"):
        committed_insurance.withdrawRansom({'from': kidnapper})


def test_return_excess_funds(committed_insurance, chain, kidnapper, friends, password):
    friends.transfer(committed_insurance, "90 ether")  # total 100 ether on insurance
    ransom = Wei("50 ether")
    initial_friends = friends.balance()
    committed_insurance.initiateRansomWithdraw(password, ransom, {'from': kidnapper})
    chain.sleep(60 * 60 * 24 * 3 + 1000)  # 3 days and 1000 seconds
    committed_insurance.withdrawRansom({'from': kidnapper})
    # 50 eth to kidnapper and friends each
    assert initial_friends + Wei("50 ether") == friends.balance()


def test_veto_full_ransom(committed_insurance, chain, kidnapper, friends, password):
    ransom = Wei("10 ether")
    initial_friends = friends.balance()
    committed_insurance.initiateRansomWithdraw(password, ransom, {'from': kidnapper})
    chain.sleep(60 * 60 * 24 * 2)  # 2 days
    committed_insurance.vetoWithdraw({'from': friends, 'value': ransom * 2})
    assert committed_insurance.balance() == 0
    assert initial_friends - 2 * ransom == friends.balance()
    chain.sleep(60 * 60 * 24 * 2)  # 2 days
    with reverts("Kidnapper: Was vetoed"):
        committed_insurance.withdrawRansom({'from': kidnapper})


def test_fuck_you(committed_insurance, kidnapper, friends, password):
    ransom = Wei("10 ether")
    committed_insurance.initiateRansomWithdraw(password, ransom, {'from': kidnapper})
    tx = committed_insurance.vetoWithdraw({'from': friends, 'value': ransom * 2})
    assert "FuckYou" in tx.events


def test_veto_refund(committed_insurance, kidnapper, friends, password):
    ransom = Wei("5 ether")
    expected_refund = committed_insurance.balance() - ransom
    initial_friends = friends.balance()
    committed_insurance.initiateRansomWithdraw(password, ransom, {'from': kidnapper})
    committed_insurance.vetoWithdraw({'from': friends, 'value': ransom * 2})
    assert initial_friends - 2 * ransom + expected_refund == friends.balance()


def test_insufficient_veto(committed_insurance, kidnapper, friends, password):
    ransom = Wei("5 ether")
    committed_insurance.initiateRansomWithdraw(password, ransom, {'from': kidnapper})
    with reverts("Kindapper: Insufficient veto amount"):
        committed_insurance.vetoWithdraw({'from': friends, 'value': ransom})


def test_veto_before_kidnap(committed_insurance, friends):
    with reverts("Kidnapper: No active ransom"):
        committed_insurance.vetoWithdraw({'from': friends, 'value': "10 ether"})
