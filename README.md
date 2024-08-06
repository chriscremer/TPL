# TPL Trader

TPL Trader is a dashboard for GMs to bid on the salaries of TPL players. With these bids, we can automatically balance the teams while taking into account the preferences of the GMs.

<img width="1535" alt="Pasted image 20240718193644" src="https://github.com/user-attachments/assets/fcba35dc-243b-41de-80e2-fb7517a9910e">

## Why?

### Salaries
Currently, the system for determining a player's salary is based on their stats for the season. This is a good heuristic but often results in players who are over/under valued. Overvalued players are difficult to acquire and undervalued players are hard to trade. 
Allowing GMs to determine the salaries of players instead of a stats-based system results in more accurate player salaries, leading to better league parity.

### Trading
The current process of trading players involves proposing numerous trades to other GMs, which often get rejected. It's a time consuming (and sometimes frustrating) process. 
Automatically determinig the trades results in less work for GMs, which hopefully makes it more enjoyable and less time consuming. A GM's job becomes accurately accessing players instead of negotiating trades.

### Summary of Benefits
- more accurate salaries + better league parity
- less work for GMs + GMs just need to access players 
- harder for GMs to hog players, if someone wants the player more. you can pay more to acquire them
- no incentive to sandbag.. if you have a good or bad game, it doesnt necessarily affect what GMs think of you 
- no complicated team cap rules based on wins and point dif. 


## What does a GM need to do?
- login once a week and adjust your bids for the players that you want to acquire/trade away
- organize your team (find subs if necessary)

Once bids are in, we run the algorithm to balance the teams while taking into account the GM preferences. 
So the job of the GMs is to accurately access the value of players in the league, along with organizing and finding subs for their games.


## How are salaries determined?
A player's salary is the average of the bids across all the GMs.


## How does the trading algorithm work?
The goal of the algorithm is to balance the teams while taking into account the preferences of the GMs.
There are a number of ways of achieving this, so we can tweak the algorithm throughout the season based on GM feedback.

Here's the current implementation for selecting a trade:
1. for each team, take the top n players with the highest difference in salary and owner bid (players you value the least)
2. for each of those players, consider the top m teams with the highest offers
3. for each of those teams, consider trading that player with players on the offering team (excluding the top n players on the offering team which they value most relative to league)
4. pick the trade that minimizes the standard deviation of the teams salaries

Another way to interpret this algorithm:
- Make a list of all possible trades
- Remove from the list trades that don't fit the GMs preferences
- Pick the trade that best balances the teams
- Repeat until teams are balanced or we've hit a limit on number of trades

## What effects would this algorithm have?
- If the demand for a player increases, their salary will increase. So if a GM wants to hold on to a in-demand player, they'll have to pay more for them. 



## FAQ

### What if I don't know the value of a player?
- Just leave it as the default value, which is the average bid of all GMs from the previous week.

### What if I'm too busy one week to update my bid on players?
- No problem, the algorithm will still balance your team. Your bids will be set to the average bid of all GMs from the previous week.

### Are there ways to exploit the algorithm?
- Possibly, but we can adjust it throughout the season to address any issues we encounter. In general, the optimal strategy will be to bid what each player is worth.

### How can we add special trade rules each week?
- We could add special bidding rules each week, for example:
  - Bid the same amount for three of the players on your team.
  - Bid the max value for five players in the league.
  - Have half your team be above some value, and the other half below that value. 



<br>
<br>


