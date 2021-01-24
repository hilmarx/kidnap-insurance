// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract KidnapInsurance {

    event Abducted(address indexed kidnapper, uint256 requestedRansom);
    event Rescued();
    event FuckYou();

    address payable public kidnapper;
    address payable public friends;
    uint256 public ransomAmount;

    uint256 public kidnappedTime;
    uint256 constant delay = 3 days;

    constructor(address payable _friends) payable {
        friends = _friends;
    }

    // Hash of the password to initiate ransom withdraw
    bytes32 constant WITHDRAW_HASH = 0x81387e6fe7c09e310810396aee0057e20224fd16320359fae10f45392cba8c80;

    // Generate a hash to show the sender knows the password. Can also be done off-chain.
    function generateHash(string memory _password) public view returns (bytes32 hash) {
        bytes32 passwordHash = keccak256(abi.encodePacked(_password));
        hash = keccak256(abi.encodePacked(msg.sender, passwordHash));
    }

    function initiateRansomWithdraw(bytes32 _hash, uint256 _ransomAmount) public {
        require(kidnapper == address(0), "Kidnapper: Already kindapped");
        require(address(this).balance >= _ransomAmount, "Kidnapper: Not enough ransom available");

        // Check if the kidnapper knows the password, front running proof
        bytes32 correctHash = keccak256(abi.encodePacked(msg.sender, WITHDRAW_HASH));
        require(correctHash == _hash, "Kidnapper: Invalid password or sender");

        // Set kidnapper/withdraw address and amount
        kidnapper = payable(msg.sender);
        ransomAmount = _ransomAmount;

        // Set date when person was kidnapped
        kidnappedTime = block.timestamp;

        emit Abducted(kidnapper, _ransomAmount);
    }

    function withdrawRansom() public {
        // Delay passed
        require(kidnappedTime + delay <= block.timestamp, "Kidnapper: Cannot withdraw yet");

        // Ransom is available
        require(address(this).balance >= ransomAmount, "Kidnapper: Was vetoed");

        // Pay Kidnappers
        kidnapper.call{value: ransomAmount}("");

        // Return any remaining funds to friends
        friends.call{value: address(this).balance}("");

        emit Rescued();
    }

    function vetoWithdraw() public payable {

        // Can only be called by trusted friend account
        require(msg.sender == friends, "Kidnapper: only friends");

        // Can only be done with an active ransom
        require(
            ransomAmount > 0 && address(this).balance - msg.value >= ransomAmount,
            "Kidnapper: No active ransom"
        );

        // Friends must pay veto amount equal to two times the ransom
        require(msg.value >= 2 * ransomAmount, "Kindapper: Insufficient veto amount");

        // Burn Veto + Ransom Amount, return rest to friends
        address(0).call{value: ransomAmount * 3}("");
        friends.call{value: address(this).balance}("");

        emit FuckYou();
    }

    receive() external payable {
        // Once the ransom amount has been set, no more funds can be deposited
        // To reset, deploy a new contract
        require(kidnapper == address(0), "Kidnapper: Can't deposit any more funds");
    }

}
