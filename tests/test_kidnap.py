from brownie import Wei, reverts


def test_rescued(insurance, chain, kidnapper, password):
    ransom = Wei("10 ether")
    initial_kidnapper = kidnapper.balance()
    password_hash = insurance.generateHash(password, {'from': kidnapper})
    insurance.initiateRansomWithdraw(password_hash, ransom, {'from': kidnapper})
    chain.sleep(60 * 60 * 24 * 3 + 1000)  # 3 days and 1000 seconds
    insurance.withdrawRansom({'from': kidnapper})
    assert initial_kidnapper + ransom == kidnapper.balance()


def test_abducted_rescued(insurance, chain, kidnapper, password):
    ransom = Wei("10 ether")
    password_hash = insurance.generateHash(password, {'from': kidnapper})
    tx = insurance.initiateRansomWithdraw(password_hash, ransom, {'from': kidnapper})
    assert "Abducted" in tx.events
    assert tx.events["Abducted"].values() == [kidnapper, ransom]

    chain.sleep(60 * 60 * 24 * 3 + 1000)  # 3 days and 1000 seconds
    tx = insurance.withdrawRansom({'from': kidnapper})
    assert "Rescued" in tx.events


def test_ransom_too_high(insurance, kidnapper, password):
    ransom = Wei("100 ether")
    password_hash = insurance.generateHash(password, {'from': kidnapper})
    with reverts("Kidnapper: Not enough ransom available"):
        insurance.initiateRansomWithdraw(password_hash, ransom, {'from': kidnapper})


def test_friends_increase_deposit(insurance, kidnapper, password, friends):
    ransom = Wei("100 ether")
    friends.transfer(insurance, "90 ether")
    password_hash = insurance.generateHash(password, {'from': kidnapper})
    insurance.initiateRansomWithdraw(password_hash, ransom, {'from': kidnapper})
    assert insurance.ransomAmount() == ransom


def test_wrong_password(insurance, kidnapper):
    password_hash = insurance.generateHash("wrong password", {'from': kidnapper})
    with reverts("Kidnapper: Invalid password or sender"):
        insurance.initiateRansomWithdraw(password_hash, "1 ether", {'from': kidnapper})


def test_frontrunning_protection(insurance, kidnapper, frontrunner, password):
    password_hash = insurance.generateHash(password, {'from': kidnapper})
    with reverts("Kidnapper: Invalid password or sender"):
        insurance.initiateRansomWithdraw(password_hash, "1 ether", {'from': frontrunner})


def test_no_early_withdraw(insurance, kidnapper, password):
    password_hash = insurance.generateHash(password, {'from': kidnapper})
    insurance.initiateRansomWithdraw(password_hash, "10 ether", {'from': kidnapper})
    with reverts("Kidnapper: Cannot withdraw yet"):
        insurance.withdrawRansom({'from': kidnapper})


def test_return_excess_funds(insurance, chain, kidnapper, friends, password):
    friends.transfer(insurance, "90 ether")  # total 100 ether on insurance
    ransom = Wei("50 ether")
    initial_friends = friends.balance()
    password_hash = insurance.generateHash(password, {'from': kidnapper})
    insurance.initiateRansomWithdraw(password_hash, ransom, {'from': kidnapper})
    chain.sleep(60 * 60 * 24 * 3 + 1000)  # 3 days and 1000 seconds
    insurance.withdrawRansom({'from': kidnapper})
    # 50 eth to kidnapper and friends each
    assert initial_friends + Wei("50 ether") == friends.balance()


def test_veto_full_ransom(insurance, chain, kidnapper, friends, password):
    ransom = Wei("10 ether")
    initial_friends = friends.balance()
    password_hash = insurance.generateHash(password, {'from': kidnapper})
    insurance.initiateRansomWithdraw(password_hash, ransom, {'from': kidnapper})
    chain.sleep(60 * 60 * 24 * 2)  # 2 days
    insurance.vetoWithdraw({'from': friends, 'value': ransom * 2})
    assert insurance.balance() == 0
    assert initial_friends - 2 * ransom == friends.balance()
    chain.sleep(60 * 60 * 24 * 2)  # 2 days
    with reverts("Kidnapper: Was vetoed"):
        insurance.withdrawRansom({'from': kidnapper})


def test_fuck_you(insurance, kidnapper, friends, password):
    ransom = Wei("10 ether")
    password_hash = insurance.generateHash(password, {'from': kidnapper})
    insurance.initiateRansomWithdraw(password_hash, ransom, {'from': kidnapper})
    tx = insurance.vetoWithdraw({'from': friends, 'value': ransom * 2})
    assert "FuckYou" in tx.events


def test_veto_refund(insurance, kidnapper, friends, password):
    ransom = Wei("5 ether")
    expected_refund = insurance.balance() - ransom
    initial_friends = friends.balance()
    password_hash = insurance.generateHash(password, {'from': kidnapper})
    insurance.initiateRansomWithdraw(password_hash, ransom, {'from': kidnapper})
    insurance.vetoWithdraw({'from': friends, 'value': ransom * 2})
    assert initial_friends - 2 * ransom + expected_refund == friends.balance()


def test_insufficient_veto(insurance, kidnapper, friends, password):
    ransom = Wei("5 ether")
    password_hash = insurance.generateHash(password, {'from': kidnapper})
    insurance.initiateRansomWithdraw(password_hash, ransom, {'from': kidnapper})
    with reverts("Kindapper: Insufficient veto amount"):
        insurance.vetoWithdraw({'from': friends, 'value': ransom})


def test_veto_before_kidnap(insurance, friends):
    with reverts("Kidnapper: No active ransom"):
        insurance.vetoWithdraw({'from': friends, 'value': "10 ether"})
