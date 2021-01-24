<h1 align=center><code>Smart Contract Kidnap Insurance</code></h1>

**Kidnap Insurance.sol** is a trustless smart contract based kidnapping insurance using Game Theory to make negotiating with kidnappers as smooth as possible.

## How it works

1. Insuree deploys the contract with the hash of a password that only they know. Optional: Fund the contract.

2. Insuree gets kidnapped. Kidnapper makes a ransom demand. Anyone can top-off the insurance contract to hold at least enough funds to cover the ransom.

3. Insuree gives the password to the kidnapper. The kidnapper generates a hash of the password and his address (off-chain or with `generateHash`) and commits the hash to the contract with `commit`. After 20 blocks, the kidnapper can call `initiateRansomWithdraw(password, ransomAmount)`. This activates a hardcoded timer (e.g. 3 days), after which the kidnapper can withdraw the ransom.

4. During the delay period, the friends of the insuree can veto the ransom payment by calling `vetoWithdraw`. Calling this functions requires a payment of two times the ransom, and it will irreversibly burn the ransom and the payed amount. 

## Good case, kidnappers release insuree:

In case the kidnappers release the insuree, the friends don't have any financial incentive to veto the ransom withdraw of the kidnappers, because they would have to pay double the amount of the ransom payment in order to prevent the kidnappers from receiving their ransom, without getting anything in return. This will provide the kidnappers with an insurance that they provides some degree of certainty that if they release the kidnapped insuree, that they will be able to withdraw the ransom (as long as the friends are rational actors and are not billionaires).

## Bad case, kidnappers don't release the insuree:

In case the kidnappers don't release the insuree within the e.g. 3 days between intiating the withdraw and actually being able to claim the ransom, the friends of the abducted insuree can veto the withdraw by burning the ransom plus the veto amount (e.g. 2k ETH). The friends will most likely only do that, if their friend (the insuree) was indeed not released, as they will have a personal interest in hurting the kidnappers financially as much as possible.

## Disclaimer

Use at own risk, not audited. This is just for fun. I hope you never have to use it :D.
