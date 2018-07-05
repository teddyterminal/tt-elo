import pandas as pd
import numpy as np
import csv
import os


def expected(A, B):
    """
    Calculate expected score of A in a match against B
    :param A: Elo rating for |player A
    :param B: Elo rating for player B
    """
    return 1 / (1 + 10 ** ((B - A) / 400))


def elo(old, exp, score, k=32):
    """
    Calculate the new Elo rating for a player
    :param old: The previous Elo rating
    :param exp: The expected score for this match
    :param score: The actual score for this match
    :param k: The k-factor for Elo (default: 32)
    """
    return old + k * (score - exp)

def run(gain, verbose = True, y = 0, vt = 5, qp = None):
    df = pd.read_csv("tt.csv")
    players = {}
    i = 0
    for line in df.iterrows():
        i+= 1
        match = line[1]
        factor = [2,2]
        winner = None
        loser = None
        try:
            winner = match["Winner"].split("/")
            loser = match["Loser"].split("/")
        except:
            winner = match["Winner"]
            loser = match["Loser"]
            factor = 1
        if (len(winner) == 1):
            factor[0] = 1
        if (len(loser) == 1):
            factor[1] = 1

        winners_prior_elo = 0
        losers_prior_elo = 0

        for player in winner:
            if player in players:
                winners_prior_elo += players[player][2]
            else:
                winners_prior_elo += 1500

        for player in loser:
            if player in players:
                losers_prior_elo += players[player][2]
            else:
                losers_prior_elo += 1500

        winners_prior_elo /= factor[0]
        losers_prior_elo /= factor[1]

        q = (match["WS"] - match["LS"])/(match["WS"] + match["LS"])
        q = q**(1/3)

        pe = 0

        if qp is None:
            pe = elo(winners_prior_elo, expected(winners_prior_elo, losers_prior_elo)*
                                   (match["WS"]+match["LS"]+ y*q*((match["WS"] - match["LS"])/3)), match["WS"], k = gain*match["WS"]/21) - winners_prior_elo

        else:
            pe = elo(winners_prior_elo, expected(winners_prior_elo, losers_prior_elo), 1,
                      k = gain*(match["WS"] - match["LS"])) - winners_prior_elo

        if pe < 0:
            pe /= 3

        if i > len(df) - vt and verbose:
            print(winner, loser, round(winners_prior_elo, 2), round(losers_prior_elo, 2), round(q, 3),
              round(expected(winners_prior_elo, losers_prior_elo)*(match["WS"]+match["LS"]), 2), round(pe, 3))

        for player in winner:
            if player in players:
                players[player] = [players[player][0] + match["WS"]/factor[0], players[player][1] + match["LS"]/factor[0],
                                   players[player][2] + pe/factor[0], players[player][3] + 1, players[player][4]]
            else:
                players[player] = [match["WS"]/factor[0], match["LS"]/factor[0], 1500 + pe/factor[0], 1, 0]

        for player in loser:
            if player in players:
                players[player] = [players[player][0] + match["LS"]/factor[1], players[player][1] + match["WS"]/factor[1],
                                   players[player][2] - pe/factor[1], players[player][3], players[player][4] + 1]
            else:
                players[player] = [match["LS"]/factor[1], match["WS"]/factor[1], 1500 - pe/factor[1], 0, 1]

    d2 = pd.DataFrame.from_dict(players, orient = 'index')
    d2.columns = ["PF", "PA", "ELO", "GW", "GL"]
    d2["D"] = d2["PF"] - d2["PA"]
    d2["PC"] = d2["D"]/(d2["PF"] + d2["PA"])
    d2.columns = ["PF", "PA", "ELO", "GW", "GL", "D", "PC"]
    d2["EXP"] = (expected(d2["ELO"], 1500)-0.5)*2
    d2["SS"] = d2["EXP"] - d2["PC"]

    points_needed = (21/(expected(d2["ELO"], 1500))).round()
    pn = []
    for i in range(len(points_needed)):
        if (points_needed[i]) < 43 and points_needed[i] > 40:
            pn.append("20-20")
        elif points_needed[i] <= 40:
            v = int(points_needed[i] - 21)
            pn.append("21-" + str(v))
        else:
            points_needed[i] = (21/(1-expected(d2.iloc[i, 2],1500))).round()
            v = int(points_needed[i] - 21)
            if(v == 20):
                pn.append("20-20")
            else:
                pn.append(str(v) + "-21")
    d2["EG"] = pn
    d2["PP"] = d2.PF + d2.PA
    d2["PCT"] = (d2.PF/d2.PP).round(3)
    d2 = d2.sort_values(by=["ELO"], ascending = False)
    d2.PCT = (d2.PF/d2.PP).round(3)
    d2.ELO = d2.ELO.round(2)
    d2.PC = d2.PC.round(2)
    d2.EXP = d2.EXP.round(2)
    d2.SS = d2.SS.round(2)
    columns = ["PP", "PF", "PA", "D", "PCT", "GW", "GL", "ELO", "PC", "EXP", "SS", "EG"]
    d2 = d2[columns]

    d2.to_csv("standings.csv")
    return d2
