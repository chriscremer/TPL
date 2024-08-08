# TPL Trader

TPL Trader is a dashboard for GMs to bid on the salaries of TPL players. With these bids, we can automatically balance the teams while taking into account the preferences of the GMs.

Website: https://tpltrader123.streamlit.app/

### Main Benefits
- more accurate player salaries -> better league parity
- GMs just need to access player value (no more negotiating trades) -> less time + more enjoyable for GMs

### Minor Benefits
- harder for GMs to hog players: if a GM wants a player, they can try to pay more to acquire them
- no incentive to sandbag: if you have a good or bad game, it doesnt necessarily affect what GMs think of you 
- no complicated team cap rules based on wins and point difference: the team's salary is the sum of its players' salaries


<img width="1535" alt="Pasted image 20240718193644" src="https://github.com/user-attachments/assets/fcba35dc-243b-41de-80e2-fb7517a9910e">


## Salaries
#### Old way:
A player's salary is based on their stats for the season. This is a good heuristic but often results in players who are over/under valued. Overvalued players are difficult to acquire and undervalued players are hard to trade. 
#### New way:
The salary of a player is the average of all the GM bids for that player. Allowing GMs to determine the salaries of players should result in more accurate player salaries, leading to better league parity.

## Trading
#### Old way:
The current process of trading players involves proposing numerous trades to other GMs, which often get rejected. It's a time consuming (and sometimes frustrating) process. 
#### New way:
We run an algorithm which automatically determines the trades by balancing the team salaries and taking into account the preferences of the GMs. This results in less work for GMs, which hopefully makes it more enjoyable and less time consuming. A GM's job becomes accurately accessing players instead of negotiating trades.



<br>
<br>



## How does the trading algorithm work?
The goal of the algorithm is to balance the teams while taking into account the preferences of the GMs.

Here's the [current implementation](https://github.com/chriscremer/TPL/blob/main/streamlit_site/algo3.py) for selecting a trade:
1. Make a list of all possible trades (exclude team captains, wildcards, etc.)
2. Pick the trade that best balances the teams (with a preference towards trades that make both teams happy)
3. Repeat until teams are balanced or we've hit a limit on number of trades

Once bids are in each week, we run the algorithm to balance the teams. So the job of a GM is to accurately access the value of the players in the league (no more negotiating trades). 
The algorithm may need some tweaking throughout the season if the GMs find that their preferences aren't being reflected in the trades.

### What effects would this algorithm have?
- If the demand for a player increases, their salary will increase. So if a GM wants to hold on to a in-demand player, they'll have to pay more for them. So it becomes harder for GMs to hog players.

  
<br>
<br>

## FAQ

### How is a player's salary determined?
- A player's salary is the average of the GM bids for that player.

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

### How will GM salaries be determined, since GMs cant be bidded on?
- We'll use a simple linear regression model to predict salary given stats.

### If we adopt this system, what does a GM need to do?
- login once a week and adjust their bids for the players that they want to acquire/trade away
- organize their team (find subs if necessary)




<br>
<br>

## TODOs

- [ ] Ability to upload/download the salaries/bids for the whole league, so GMs can write their bids in a excel sheet then upload instead of using all the sliders
- [ ] Add all player stats to the site
- [ ] Show change in player salary over time

<br>
<br>
<br>
<br>


## Tell Me More

In case you want to know exactly how the algorithm works, [here](https://github.com/chriscremer/TPL/blob/main/streamlit_site/algo3.py) is the location of the code. 

The main thing the algo is doing is making a list of all possible trades, then picking the one that reduces the standard deviation of the team salaries (bring all team salaries closer to the average).
The question is: how do we take into consideration the preferences/bids of the GMs?

Currently, GM preferences come into the algorithm in two ways:
1. protecting your most valued players
2. prioritizing happy trades 

### What are "your most valued players"?










