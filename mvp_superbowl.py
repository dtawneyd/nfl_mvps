from bs4 import BeautifulSoup as Soup
from pandas import DataFrame
import pandas as pd
import requests

# scraping data from website using requests and BeautifulSoup for NFL MVPs and Superbowl MVPs
# this section of code scraps a table that was found showing NFL MVPs by year and player name
league = requests.get('https://eatdrinkandsleepfootball.com/history/awards/mvp.html')
league_soup = Soup(league.text, features='lxml')
league_table = league_soup.find_all('table')  # finding all tags labeled table for choosing table in next line
league_table = league_table[0]  # choosing the first table on website
league_rows = league_table.find_all('tr')  # finding all tags labeled tr to find table rows

# this section of code scraps a table that was found showing NFL Superbowl MVPs
superbowl = requests.get('https://www.foxsports.com/nfl-super-bowl-mvps')
superbowl_soup = Soup(superbowl.text, features='lxml')
superbowl_table = superbowl_soup.find_all('table')
superbowl_table = superbowl_table[0]
superbowl_rows = superbowl_table.find_all('tr')


# this function was written to take the league_rows and superbowl_rows bs4 objects and convert them to python strings
def parse_row(row):
    return [str(x.string) for x in row.find_all('td')]


# using the parse_row function and DataFrame method from Pandas, takes the
# Superbowl MVP table as a python string and converts it into a Pandas dataframe
list_parsed_superbowl = [parse_row(row) for row in league_rows[1:]]
league_mvp = DataFrame(list_parsed_superbowl)

# the following code was written to clean and manipulate the Superbowl MVP data for merging later
league_mvp.columns = ['year', 'league_mvp']  # setting the name of the columns
league_mvp.sort_values('year', ascending=True, inplace=True)  # sorting the table by year
league_mvp = league_mvp[9:]  # this slice eliminates the league MVPs that were awarded before first Superbowl

# the following code was written to split the league_mvp column data into two separate columns and remove unwanted
# characters in the league_mvp columns (i.e. "NFL: " before the player name)
league_mvp['mvp_team'] = (league_mvp['league_mvp'].apply(lambda x: x.split(', ')[-1]))
league_mvp['league_mvp'] = (league_mvp['league_mvp'].apply(lambda x: x.split(', ')[0]))
league_mvp['league_mvp'] = league_mvp['league_mvp'].str.replace('NFL: ', '')

# using the parse_row function and DataFrame method from Pandas, takes the
# League MVP table as a python string and converts it into a Pandas dataframe
list_parsed_mvp = [parse_row(row) for row in superbowl_rows]
superbowl_mvp = DataFrame(list_parsed_mvp)

# the following code was written to clean and manipulate the League MVP data for merging later
superbowl_mvp.columns = ['superbowl', 'year', 'superbowl_mvp', 'position', 'winning_team']  # naming the columns
superbowl_mvp = superbowl_mvp[1:]  # slicing to remove first row of irrelevant data
superbowl_mvp.set_index('superbowl', inplace=True)  # setting index to Superbowl number
superbowl_mvp.drop('position', axis=1, inplace=True)  # dropping the position columns
superbowl_mvp['winning_team'] = (superbowl_mvp['winning_team'].apply(lambda x: x.split(' ')[-1]))  # removing team name
# from winning_team (i.e. "Packers" from "Green Bay Packers" to match team name format in league MVP table

# the following line of code merges the league_mvp and superbowl_mvp dataframes using the "year" column
df = pd.merge(league_mvp, superbowl_mvp, on='year')

# here is where I wanted to figure out how often the MVPs matched in a year. A new column ('league_and_superbowl') was
# created as a boolean column checking whether the player that won league MVP also won Superbowl MVP and checking for
# and then finding the percentage of times that has happened and rounding to 1 significant figure.
df['league_and_superbowl'] = df['league_mvp'] == df['superbowl_mvp']
same_player = df['league_and_superbowl'] == True
average = round((same_player.mean() * 100), 1)

# print statement giving the average
print(f'Since the first NFL Superbowl, the NFL MVP has also won the Superbowl MVP {average}% of the time!')
