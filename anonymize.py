import pandas as pd
from anon_map import anon_map

def anonymize_tt():
    df = pd.read_csv("tt.csv")
    for i, game in df.iterrows():
        x = df.loc[i, "Winner"].split("/")
        for j in range(len(x)):
            x[j] = anon_map[x[j]]
        if len(x) > 1:
            x = x[0] + "/" + x[1]
        else:
            x = x[0]

        df.loc[i, "Winner"] = x

        x = df.loc[i, "Loser"].split("/")
        for j in range(len(x)):
            x[j] = anon_map[x[j]]
        if len(x) > 1:
            x = x[0] + "/" + x[1]
        else:
            x = x[0]

        df.loc[i, "Loser"] = x

    df.to_csv("anonymized_tt.csv")

def anonymize_standings():
    df = pd.read_csv("standings.csv")
    for i, player in df.iterrows():
        df.loc[i, "Unnamed: 0"] = anon_map[df.loc[i, "Unnamed: 0"]]
    df.to_csv("anonymized_standings.csv")

anonymize_tt()
anonymize_standings()
