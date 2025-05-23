# TPL Trader

TPL Trader is a dashboard for GMs to bid on the salaries of TPL players. With these bids, we can automatically balance the teams while taking into account the preferences of the GMs.

Website: https://tpltrader123.streamlit.app/

### Main Benefits
- more accurate player salaries -> better league parity
- automated trading -> less time + more enjoyable for GMs

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

### Notes:
- Currently, the algorithm is capped at max 3 trades per team per week. This is to prevent too much roster turnover.
- Before the algorithm runs, we'll normalize the salaries so that the average salary is max_salary/2. We do this to keep the total cap of the league constant throughout the season. 

So each week, once the bids are in:
- Calculate the new salaries for each player: the average of the GM bids
- Normalize the salaries so that the average salary is max_salary/2 (currently max_salary = 1000, so the average salary will be 250)
- Run the algorithm to balance the teams
- Update the rosters





<br>
<br>
<br>
<br>


## Tell Me More

In case you want to know exactly how the algorithm works, [here](https://github.com/chriscremer/TPL/blob/main/streamlit_site/algo3.py) is the location of the code. 

The main thing the algo is doing is making a list of all possible trades, then picking the one that reduces the standard deviation of the team salaries (bring all team salaries closer to the average).

### What excludes a trade from being considered?
- If a trade increases the standard deviation of the team salaries (reduces parity), it's excluded
- If a player is a team captain, they can't be traded
- If a player is a wildcard, they can't be traded (this could possibly be changed at some point)
- Trades must be of the same gender

### How do we take into consideration the preferences/bids of the GMs?

Currently, GM preferences come into the algorithm in two ways:
1. protecting your most valued players
2. prioritizing happy trades 

### What are "your most valued players"?

We'll define the value of a player to a GM as: **GM bid - Average bid**, for that player.

So if the average bid for a player is 5, and I bid 20 for that player, the value of that player to me is 15.
Your most valued players are the players with the highest value to you, which is not necessarily the players with the highest salary on your team.

### How are most valued players protected?

When the algorithm is making a list of all possible trades, it will exclude your most valued players from the list. This means that the algorithm will never trade away your most valued players.

It's currently set to protect your top **2** most valued players, but this can be adjusted.

### Does this mean I can protect the same player all season?

Not necessarily. To protect a player, you need to bid higher on them than the average bid. By bidding higher on them, you're increasing their salary for next week, which means you'll have to pay more to keep them. So if you want to keep a player all season, you'll likely have to keep increasing their salary.


### What are "happy trades"?

A happy trade is a trade where both GMs think they're receiving a player that is worth more than the player they're giving up. 

<p align="center">
  <b>
  Happiness = (my bid for the player I'm receiving) - (my bid for the player I'm giving up)
  </b>
</p>

For example, I have John Smith on my team and you have Zack Brown. I think John Smith is worth 40 and Zack Brown is worth 50, whereas you think John Smith is worth 60 and Zack Brown is worth 30. If we trade John Smith for Zack Brown, I receive a player that I think is worth 10 more than the player I'm giving up, and you receive a player that you think is worth 30 more than the player you're giving up. So this is a happy trade because we both think we're receiving a player that is worth more than the player we're giving up.


### How does the algorithm prioritize "happy trades"?

If there are any happy trades available, the algorithm will pick the happy trade that reduces the standard deviation of the team salaries the most.

### What if there are no happy trades available?

If there are no happy trades available, the algorithm will look for "somewhat happy trades". A "somewhat happy trade" is a trade where the sum of the happiness of the two GMs is positive. 

So if I'm giving up a player I think is worth 40 and receiving a player I think is worth 30, my happiness is -10. If you're giving up a player you think is worth 20 and receiving a player you think is worth 50, your happiness is 30. The sum of our happiness is 20, so this is a "somewhat happy trade".

If there are no happy trades available, the algorithm will pick the somewhat happy trade that reduces the standard deviation of the team salaries the most.

### What if there are no happy or somewhat happy trades available?

If there are no happy or somewhat happy trades available, the algorithm will pick the trade that reduces the standard deviation of the team salaries the most.
In other words, the algorithm will simply try to balance the teams (increase parity) regardless of what the GMs bid.



<br>
<br>
<br>
<br>
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


### What effects would this algorithm have?
- If the demand for a player increases, their salary will increase. So if a GM wants to hold on to a in-demand player, they'll have to pay more for them. So it becomes harder for GMs to hog players.
- If the demand for a player is low, their salary will decrease, which should increase the demand for them. The result is players being accurately valued.
- If a player has a good, bad or misses a game, it doesn't necessarily affect what GMs think of them, so their salary doesn't necessarily change. Additionaly, there's no incentive to sandbag.




###	What ability does a GM have to control their roster? There’s a lots of elements to consider when putting together a roster (skill sets, personalities, areas of strength or weakness currently present on the team, etc.) and at some point roster stability counts for a lot. 

- One way a GM can control their roster is by protecting their most valued players. See: [How are most valued players protected?](#how-are-most-valued-players-protected)
- GMs can also bid low on players they want to trade away, and high on players they want to acquire. This will increase the likelihood of the algorithm making the trades they want. See: [How do we take into consideration the preferences/bids of the GMs?](#how-do-we-take-into-consideration-the-preferencesbids-of-the-gms)


### Could this system lead to increased trade activity and roster turnover?

- Currently, the algorithm is capped at max 3 trades per team per week. This is to prevent too much roster turnover. 
- We could reduce this number throughout the season to reduce roster turnover.

###	What if two (or more) GMs bid the same amount?

- There are a number of factors that the algorithm will consider to determine which trade is made:
  - First, the algorithm will prioritize trades that make both teams happy. So it depends what players are on your roster and what the other GMs are bidding for them.
  - If the bids are all equal, the algorithm will prioritize trades that reduce the standard deviation of the team salaries the most. So your team's salary will be the deciding factor.
  - If all of those are equal (very rare), then the algorithm will randomly pick one of the trades.


### Is this dynamic pricing or ebay pricing? If someone is traded away during a trading session could I change my bid to try and get them back?

- This is ebay pricing / blind bidding. You can adjust your preferences during some time period, then once the time is up the algorithm will run and determine the trades. So you can't adjust your bids based on what other GMs are doing. Ideally, you should bid what you think each player is worth so that you acquire players that you think are undervalued and trade away players that you think are overvalued.

### Does this system leave me open to having injured or absent players traded to my team?

- Yes this is possible, but you can reduce the likelihood of this happening by bidding low on players you don't want to acquire. 


<br>
<br>
<br>
<br>
<br>
<br>


## TODOs

- [ ] Ability to upload/download the salaries/bids for the whole league, so GMs can write their bids in a excel sheet then upload instead of using all the sliders
- [ ] Add all player stats to the site
- [ ] Show change in player salary over time












