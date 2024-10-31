# TPL Trader



Website: https://tpltrader123.streamlit.app/



## How does the trading algorithm work?
The goal of the algorithm is to balance the teams while taking into account the preferences of the GMs.

At a high level, the algorithm works like this:
1. Make a list of all possible trades (exclude team captains, wildcards, etc.)
2. Pick the trade that best balances the teams (with a preference towards trades that make both teams happy)
3. Repeat until teams are balanced or we've hit a limit on number of trades

Once bids are in each week, we run the algorithm to balance the teams. So the job of a GM is to accurately access the value of the players in the league (no more negotiating trades). 

### Notes:
- You can protect two players, they will not be traded.
- The total of all your overbids can't be above 10k, and the total of all your underbids can't be below -10k. 
- The algorithm is capped at max 4 trades per team per week. This is to prevent too much roster turnover.



<br>


## More details on how the algorithm works

### Acceptable Trades

The first step is to make a list of all acceptable trades. A trade is not acceptable if:
- A trade increases the standard deviation of the team salaries (reduces parity)
- A player is protected, a team captain, or a wildcard
- A trade is between difference genders

### How does it take into consideration the preferences/bids of the GMs?

After making a list of all acceptable trades, the algorithm groups the trades into three categories:
1. Happy trades
2. Somewhat happy trades
3. Neutral trades


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



### Code
In case you want to know exactly how the algorithm works, [here](https://github.com/chriscremer/TPL/blob/main/streamlit_site/algo4.py) is the location of the code. 

<br>
<br>
<br>
<br>
<br>
<br>








