## Summary
`enterRaffle` function uses gas inefficient duplicate check that causes leads to Denial of Service, making subsequent participants to spend much more gas than previous users to enter.
## Vulnerability Details
In the `enterRaffle` function, to check duplicates, it loops through the `players` array.  As the `player` array grows, it will make more checks, which leads the later user to pay more gas than the earlier one. More users in the Raffle, more checks a user have to make leads to pay more gas.

## Impact
As the arrays grows significantly over time, it will make the function unusable due to block gas limit. This is not a fair approach and lead to bad user experience.

## POC
In existing test suit, add this test to see the difference b/w gas for users.
once added run `forge test --match-test testEnterRaffleIsGasInefficient -vvvvv` in terminal. you will be able to see logs in terminal.
```solidity
function testEnterRaffleIsGasInefficient() public {
  vm.startPrank(owner);
  vm.txGasPrice(1);
 
  /// First we enter 100 participants
  uint256 firstBatch = 100;
  address[] memory firstBatchPlayers = new address[](firstBatch);
  for(uint256 i = 0; i < firstBatchPlayers; i++) {
    firstBatch[i] = address(i);
  }

  uint256 gasStart = gasleft();
  puppyRaffle.enterRaffle{value: entranceFee * firstBatch}(firstBatchPlayers);
  uint256 gasEnd = gasleft();
  uint256 gasUsedForFirstBatch = (gasStart - gasEnd) * txPrice;
  console.log("Gas cost of the first 100 partipants is:", gasUsedForFirstBatch);

  /// Now we enter 100 more participants
  uint256 secondBatch = 200;
  address[] memory secondBatchPlayers = new address[](secondBatch);
  for(uint256 i = 100; i < secondBatchPlayers; i++) {
    secondBatch[i] = address(i);
  }
  
  gasStart = gasleft();
  puppyRaffle.enterRaffle{value: entranceFee * secondBatch}(secondBatchPlayers);
  gasEnd = gasleft();
  uint256 gasUsedForSecondBatch = (gasStart - gasEnd) * txPrice;
  console.log("Gas cost of the next 100 participant is:", gasUsedForSecondBatch);
  vm.stopPrank(owner);

}
```
## Tools Used
Manual Review, Foundry
## Recommendations
Here are some of recommendations, any one of that can be used to mitigate this risk.

1. User a mapping to check duplicates. For this approach you to declare a variable `uint256 raffleID`, that way each raffle will have unique id. Add a mapping from player address to raffle id  to keep of users for particular round.

```diff
+ uint256 public raffleID;
+ mapping (address => uint256) public usersToRaffleId;
.
.
function enterRaffle(address[] memory newPlayers) public payable {
        require(msg.value == entranceFee * newPlayers.length, "PuppyRaffle: Must send enough to enter raffle");
        for (uint256 i = 0; i < newPlayers.length; i++) {
            players.push(newPlayers[i]);
+           usersToRaffleId[newPlayers[i]] = true;
        }
        
        // Check for duplicates
+       for (uint256 i = 0; i < newPlayers.length; i++){
+           require(usersToRaffleId[i] != raffleID, "PuppyRaffle: Already a participant");

-        for (uint256 i = 0; i < players.length - 1; i++) {
-            for (uint256 j = i + 1; j < players.length; j++) {
-                require(players[i] != players[j], "PuppyRaffle: Duplicate player");
-            }
        }

        emit RaffleEnter(newPlayers);
    }
.
.
.

function selectWinner() external {
        //Existing code
+    raffleID = raffleID + 1;        
    }
```