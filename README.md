<h1 align=center><code>Smart Contract Kidnap Insurance</code></h1>

**Kidnap Insurance.sol** is a trustless smart contract based kidnapping insurance using Game Theory to make negotiating with kidnappers as smooth as possible.

## How it works

1. Insuree pays in a ransom amount that only an address that he / she controls can withdraw (kidnapper). Insuree must memorize the private key of this address or have access to it when being kidnapped. Insuree also sets an address which is a multisig controlled by his / her friends

2. Insuree gets kidnapped. He / she gives the kidnapper access to the private key being labelled `kidnapper`. Kidnapper can now call the `initiateRansomWithdraw` function, which activates an e.g. 3 day timer. After the 3 days have passed the kidnappers can withdraw the ransom

3. Within the 3 day period, the friends of the kidnapped person can veto the ransom payment by calling `vetoWithdraw`. However, this function is very costly to call. For example, if the ransom that was paid in by the kidnapped insuree is 1k ETH, then the veto would cost the friends 2k ETH to cast. This 2k veto payment will be burned alongside the original e.g. 1k ransom payment.

## Good case, kidnappers release insuree:

In case the kidnappers release the insuree, the friends don't have any financial incentive to veto the ransom withdraw of the kidnappers, because they would have to pay double the amount of the ransom payment in order to prevent the kidnappers from receiving their ransom, without getting anything in return. This will provides the kidnappers with an insurance that they know if they release the kidnapped insuree, that they will be able to withdraw the ransom (as long as the friends are rational actors and are not billionaires).

## Bad case, kidnappers don't release the insuree:

In case the kidnappers don't release the insuree within the e.g. 3 days between intiating the withdraw and actually being able to claim the ransom, the friends of the abducted insuree can veto the withdraw by burning the ransom plus the veto amount (e.g. 2k ETH). The friends will most likely only do that, if their friend (the insuree) was indeed not released, as they will have a personal interest in hurting the kidnappers financially as much as possible.

## Disclaimer

Use at own risk, not audited. This is just for fun. I hope you never have to use it :D.