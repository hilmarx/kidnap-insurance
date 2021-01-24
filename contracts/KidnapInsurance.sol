// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract KidnapInsurance {

    event Abducted();
    event Rescued();
    event FuckYou();

    address public kidnapper;
    address public friends;
    address payable public ransomReceiver;

    uint256 public kidnappedTime;
    bool public vetoed;

    uint256 constant ransom = 1000e18; // 1k ETH
    uint256 constant veto = 2000e18; // 2k ETH
    uint256 constant delay = 3 days; // 3 days

    modifier onlyKidnapper() {
        require(msg.sender == kidnapper, "Kidnapper: only kidnapper");
        _;
    }

    modifier onlyFriends() {
        require(msg.sender == friends, "Kidnapper: only friends");
        _;
    }

    constructor(address _kidnapper, address _friends) payable {
        require(msg.value == ransom, "Kidnapper: Deposit must be ransom");
        kidnapper = _kidnapper;
        friends = _friends;
    }

    // Kidnapper Funcs
    function initiateRansomWithdraw(address payable _receiver) onlyKidnapper public {
        // Must be first kidnapp
        require(kidnappedTime == 0, "Kidnapper: Already kindapped");

        // Not vetoed yet
        require(!vetoed, "Kidnapper: Was vetoed");

        // Set date when person was kidnapped
        kidnappedTime = block.timestamp;

        // Set receiver of ransom to avoid withdraw front running
        ransomReceiver = _receiver;

        emit Abducted();
    }

    function withdrawRansom() public {
        // Victim was rescued
        require(!vetoed, "Kidnapper: Was vetoed");

        // Delay passed
        require(kidnappedTime + delay <= block.timestamp, "Kidnapper: Cannot withdraw yet");

        // Pay Kidnappers
        ransomReceiver.call{value: ransom}("");

        emit Rescued();
    }

    // Friends Funcs
    function vetoWithdraw() onlyFriends public payable {
        // Friends must pay veto amount
        require(msg.value == veto, "Kindapper: Insufficient veto amount");
        require(address(this).balance >= veto + ransom, "Kindapper: Ransom already withdrawn");

        // Burn Veto + Ransom Amount
        address(0).call{value: veto + ransom}("");

        // Kindapper cannot withdraw funds
        vetoed = true;

        emit FuckYou();
    }
}