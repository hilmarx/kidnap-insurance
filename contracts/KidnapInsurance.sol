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

    mapping(address => bytes32) public commitHash;
    mapping(address => uint256) public commitBlock;

    constructor(address payable _friends) payable {
        friends = _friends;
    }

    // Hash of the password to initiate ransom withdraw
    bytes32 constant WITHDRAW_DOUBLE_HASH = 0x9cf155a4335783b44436382cfb25875ff1ffa6c2911e40027434218cf7522b79;

    // Generate a hash to show the sender knows the password. Can also be done off-chain.
    function generateHash(string memory _password) public view returns (bytes32 hash) {
        bytes32 passwordHash = keccak256(abi.encodePacked(_password));
        hash = keccak256(abi.encodePacked(msg.sender, passwordHash));
    }

    function commit(bytes32 _hash) public {
        commitHash[msg.sender] = _hash;
        commitBlock[msg.sender] = block.number;
    }

    function initiateRansomWithdraw(string memory _password, uint256 _ransomAmount) public {
        require(kidnapper == address(0), "Kidnapper: Already kindapped");
        require(address(this).balance >= _ransomAmount, "Kidnapper: Not enough ransom available");

        // Check if the kidnapper knows the password, front running proof
        bytes32 passwordHash = keccak256(abi.encodePacked(_password));
        bytes32 passwordDoubleHash = keccak256(abi.encodePacked(passwordHash));
        bytes32 commitHash_ = keccak256(abi.encodePacked(msg.sender, passwordHash));

        require(passwordDoubleHash == WITHDRAW_DOUBLE_HASH, "Kidnapper: Invalid password or sender");
        require(commitHash_ == commitHash[msg.sender], "Kidnapper: Commit hash first");
        require(block.number > commitBlock[msg.sender] + 20, "Kidnapper: No front running");

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
