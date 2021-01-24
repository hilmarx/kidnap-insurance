from brownie import reverts


def test_commit(insurance, kidnapper, password):
    commit_hash = insurance.generateHash(password, {'from': kidnapper})
    tx = insurance.commit(commit_hash, {'from': kidnapper})
    assert insurance.commitHash(kidnapper) == commit_hash
    assert insurance.commitBlock(kidnapper) == tx.block_number


def test_ransom_succeeds(insurance, chain, kidnapper, password):
    commit_hash = insurance.generateHash(password, {'from': kidnapper})
    insurance.commit(commit_hash, {'from': kidnapper})
    chain.mine(25)
    tx = insurance.initiateRansomWithdraw(password, "1 ether", {'from': kidnapper})
    assert "Abducted" in tx.events


def test_no_commit(insurance, kidnapper, password):
    with reverts("Kidnapper: Commit hash first"):
        insurance.initiateRansomWithdraw(password, "1 ether", {'from': kidnapper})


def test_wrong_password(insurance, chain, kidnapper):
    password = "wrong password"
    commit_hash = insurance.generateHash(password, {'from': kidnapper})
    insurance.commit(commit_hash, {'from': kidnapper})
    chain.mine(25)
    with reverts("Kidnapper: Invalid password or sender"):
        insurance.initiateRansomWithdraw(password, "1 ether", {'from': kidnapper})


def test_no_frontrunning(insurance, frontrunner, password):
    commit_hash = insurance.generateHash(password, {'from': frontrunner})
    insurance.commit(commit_hash, {'from': frontrunner})
    with reverts("Kidnapper: No front running"):
        insurance.initiateRansomWithdraw(password, "1 ether", {'from': frontrunner})
