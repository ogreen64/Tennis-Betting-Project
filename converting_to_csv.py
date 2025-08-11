import json
import pandas as pd

with open('ATP_Matches_2020-08-31.json', 'r') as file:
    my_list_1 = json.load(file)
with open('ATP_Matches_2024-08-26.json', 'r') as file:
    my_list_2 = json.load(file)

my_list_final = my_list_1 + my_list_2

df = pd.DataFrame(my_list_final, columns=['Player 1','Player 2','Player 1 Ranking','Player 2 Ranking',
                                          'Player 1 Age','Player 2 Age','Player 1 Points','Player 2 Points',
                                          'Round','Tournament','Surface','Match Length','Date',
                                          'Probability Player 1 Wins'])
df.to_csv('ATP_Matches.csv', index=False)