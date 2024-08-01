# TPL Trader

TPL Trader is a dashboard for GMs to bid on the salaries of TPL players. With these bids, we can automatically balance the teams while taking into account the preferences of the GMs.

<img width="1535" alt="Pasted image 20240718193644" src="https://github.com/user-attachments/assets/fcba35dc-243b-41de-80e2-fb7517a9910e">

## Why?

### Salaries
Currently, the system for determining a player's salary is based on their stats for the season. This is a good heuristic but often results in players who are over/under valued. Overvalued players are difficult to acquire and undervalued players are hard to trade. 
Allowing GMs to determine the salaries of players instead of a stats-based system results in more accurate player salaries, leading to better league parity.

### Trading
The current process of trading players involves proposing numerous trades to other GMs, which often get rejected. It's a tedious process. 
less work for GMs, hopefully more enjoyable and less time consuming. your job becomes accurately accessing players 
If you're busy once week, dont need to do anything .. 

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


## What effects would this have?
- If the demand for a player increases, their salary will increase. So if a GM wants to hold on to a in-demand player, they'll have to pay for them. 

<br>
<br>
<br>


