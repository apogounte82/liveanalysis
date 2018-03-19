# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 16:23:10 2018

@author: tolaros
"""

# Importing our libraries
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sb
from pandas import Series, DataFrame

# Reading our dataset
dataset = pd.read_excel('LIVE1STHALF.xlsx')

# Our goal is to explore the possibility of placing live bets , during the first half of  a 
# football game, and particularly after the 35th minute.In other words we want to predict 
# a late first half goal. But first let's explore our data
dataset.head()
dataset.shape
dataset = dataset.drop_duplicates()
dataset.isnull().sum()
# We will drop the rows with missing values in particular columns
dataset.dropna(subset = ['HAT_GL','NEWHNDCP','ODD40ROUNDED', 'G37', 'G38' , 'G39'] , inplace = True)

# Let's verify
dataset.isnull().sum()



# Now, we create a column with the sum of goals scored at the 37th mimute. H37 is Home goals at 37th minute, A37 
# stands for Away goals at 37th minute. Respectively, H38 , A38 for the 38th minute, etc
dataset['goalssum37'] = dataset['H37'] + dataset['A37']
dataset['goalssum38'] = dataset['H38'] + dataset['A38']
dataset['goalssum39'] = dataset['H39'] + dataset['A39']
dataset['goalssum40'] = dataset['H40'] + dataset['A40']

# We will verify the "obvious". As we proceed to the end of the half time, no matter what the score
# is, the probability of a goal being scored decreases(???)

prob37 = dataset['G37'].mean()
prob38 = dataset['G38'].mean()
prob39 = dataset['G39'].mean()
prob40 = dataset['G40'].mean()

probs = [prob37,prob38,prob39,prob40]
minutes = [37,38,39,40]

probsdf = DataFrame()
probsdf['minutes'] = minutes
probsdf['probs'] = probs
sb.regplot(x= 'minutes' , y = 'probs' , data = probsdf)

# There seems to be a strong negative correlation. 
from scipy.stats.stats  import pearsonr
pearsonr(probsdf['minutes'] , probsdf['probs'])

# Of course, the probability should change , depending on the exelixis of the match so far. 
# We will create a pivot table to detect  the probabibility for all the scores at 37th minute
# But first let's see the frequency of the sum of goals at 37th minute
dataset['goalssum37'].value_counts().plot(kind = 'bar')

# As we can see, 4+ goals is very rare. Let's make  subset, that contains only 3 goals or less
subset37 = dataset[dataset['goalssum37'] <= 3]



# For every possible score at the 37th  minute, we will get the probability of a goal scored 
# till the end of 1st half.We will use a pivot table.
subset37.pivot_table(index = ['H37', 'A37'] , values = 'G37').plot(kind = 'bar')

# It would be fair to say that, for instance, if the score is 2-0 at 37th minute
#(the prob of a goal being scored is 27.7%), if the offered odd is greater than 1/0.277 = 3.6,
# then I should place a bet. But what about the offered odds, at 37th minute? Let us see the 
# distribution. The'OD37' column, contains the odds we are interested in.twonil is a subset, 
# where the score at the 37th minute is 2-0

twonil = subset37[subset37['H37'] == 2][subset37['A37'] == 0]
twonil['OD37'].value_counts().sort_index().plot(kind = 'bar')
# We could say that it reminds somehow of a normal distribution. Some metrics
twonil['OD37'].mean()
twonil['OD37'].std()
# Maybe we have a chance, because the mean odd is very close to the fair odd. Let's calculate our ROI, 
# assuming that we bet 1 euro at each game that  is 2-0 at 37th minute and the offered odd is equal 
# or greater than 3.6
twonilfairodds = twonil[twonil['OD37'] >3.59]

# If agoal IS scored, the G37 column has a value of 1.If no goal is scored then G37 has a value of 0. So I will
# make a new column,named profit, multiplying G37 with the offered odd. The sum of this column, will be the 
# money returned to us.
twonilfairodds['profit'] = twonilfairodds['G37'] * twonilfairodds['OD37']
ROI = (twonilfairodds['profit'].sum() / len(twonilfairodds['profit'])) -1 
print(ROI) # So close but negative


# Next, let us try something difficult. Imagine a game that is  0-0  at the 40th minute. Which factors
# could be critical for the prognosis of a goal being scored? Info from the bookies? In play stats?
# BOTH?

# Construction of a subset neilneil40
neilneil40 = dataset[dataset['H40'] == 0][dataset['A40'] == 0]
neilneil40.shape

# let's start with what the bookmaker has to offer. HAT_GL is  the asian half time goal line. 
# Usually the greater it is, the more possible it is that there will be goalsin the 1st half 

neilneil40['HAT_GL'].value_counts()
plt.hist(neilneil40['HAT_GL'], range = (0.5, 2.25), bins=15)
# Let's see a graph of the probability and each HAT_GL price
pv40 = neilneil40.pivot_table(index = 'HAT_GL' , values = 'G40')
pv40['HAT_GL'] = pv40.index
sb.regplot(x= 'HAT_GL' , y = 'G40' , data = pv40 )
# WE detect a positive correlation, but remember EVERYTHING is a matter of value. For example, 
# if HAT_GL = 1.5 ,there is a 24.32 %( fair odd 4.11)  chance that a goal will be scored. But, 
# what is the odd,  for this circumstance? Let us see
neilneil40test = neilneil40[neilneil40['HAT_GL'] == 1.5]
# the 'ODD40ROUNDED' column, contains the odds ata 40th minute, with a 0.5 step (3,3.5,4,4.5,etc)
neilneil40test['ODD40ROUNDED'].value_counts()
plt.hist(neilneil40test['ODD40ROUNDED'], range=(3,6), bins = 12)

# We can assume that maybe there is a chance, because the majority of the offered odds is around 4.5
# a little bot greater than the fair odd. We will create a subset, where the odds are at least 4.5
fairodds = neilneil40test[neilneil40test['ODD40ROUNDED'] >4.49]
fairodds['ODD40ROUNDED'].value_counts().plot(kind = 'bar')
pv = fairodds.pivot_table(index = 'ODD40ROUNDED' , values = 'G40')
pv['ODD40ROUNDED'] = pv.index
sb.regplot(x= 'ODD40ROUNDED' , y = 'G40' , data = pv )

# If agoal IS scored, the G40 column has a value of 1. So I will make a new column, multiplying
# G40 with the offered odd. The sum of this column, will be the money returned to us.

fairodds['profit'] = fairodds['G40'] * fairodds['ODD40ROUNDED']
ROI = (fairodds['profit'].sum() / len(fairodds['profit'])) -1 
print(ROI)

# So there is a positive ROI of 1.68%

# Now we will do the same for the GL column. This is the asian handicap for the 90 minutes sum of goals
# Again the greater it is , more goals will probably be scored
neilneil40['GL'].value_counts()
plt.hist(neilneil40['GL'], range = (1.5, 5.5), bins=16)

# Let's see a graph of the probability and each GL price
pvGL = neilneil40.pivot_table(index = 'GL' , values = 'G40')
pvGL['GL'] = pvGL.index
sb.regplot(x= 'GL' , y = 'G40' , data = pvGL ) # positive and strong correlation
pearsonr(pvGL['GL'], pvGL['G40'])

# We will do all of the above for the ODD40ROUNDED column. We have the odds at 40th minute, 
# rounded at 0.5 level.
neilneil40['ODD40ROUNDED'].value_counts()
plt.hist(neilneil40['ODD40ROUNDED'], range = (3, 9), bins=12)
# We will narrow the prices of 'ODD40ROUNDED' between 4 and 8
narrowed = neilneil40[neilneil40['ODD40ROUNDED'] < 8][neilneil40['ODD40ROUNDED']  >3.99]

# Let's see a graph of the probability and each ODD40ROUNDED price
pvODD = narrowed.pivot_table(index = 'ODD40ROUNDED' , values = 'G40')
pvODD['ODD40ROUNDED'] = pvODD.index
sb.regplot(x= 'ODD40ROUNDED' , y = 'G40' , data = pvODD ) 
pearsonr(pvODD['ODD40ROUNDED'], pvODD['G40'])

 # strong negative correlation, as expected


# Next, I want to investigate a simple belief. Does the probability of a goal being scored increase,
# while the totalshots made by the two teams increase? I will create three new columns, total shots on 
# target, total shots off target, and total shots
neilneil40['totshoton'] = neilneil40['SoTH40'] + neilneil40['SoTA40']
neilneil40['totshotoff'] = neilneil40['SofH40'] + neilneil40['SofA40']
neilneil40['totshots'] = neilneil40['totshoton'] + neilneil40['totshotoff']

# Exploration of totshoton
neilneil40['totshoton'].value_counts().sort_index().plot(kind = 'bar')
# We will drop all games that have more than 8 shots on target, beacuse they have very very low frequency
subset = neilneil40[neilneil40['totshoton'] < 9]
pvshon = subset.pivot_table(index = 'totshoton' , values = 'G40')
pvshon['totshoton'] = pvshon.index
sb.regplot(x= 'totshoton' , y = 'G40' , data = pvshon ) 
pearsonr(pvshon['totshoton'], pvshon['G40']) # very strong correlation

# Exploration of subset2, where totshoton = 6 and probability is 22.56 %,meaning a fair odd would be 4.43

subset2 = subset[subset['totshoton'] == 6]
subset2['ODD40ROUNDED'].mean()
subset2['ODD40ROUNDED'].value_counts().sort_index().plot(kind = 'bar')
# The majority of the offerd odds are between 4.5 and 6.5, with a mean value of 5.16, which is above fair
# Let us now evaluate the ROI, if we placed a bet on each game with an odd greater or equal to 4.5
fairodds2 = subset2[subset2['ODD40ROUNDED'] >4.49]
fairodds2['profit'] = fairodds2['G40'] * fairodds2['ODD40ROUNDED']
ROI = (fairodds2['profit'].sum() / len(fairodds2['profit'])) -1  # 8% ROI






