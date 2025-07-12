import os

import condorcet
import pandas as pd

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))


def excel_to_preferences(excel_file):
    df = pd.read_excel(excel_file)
    candidates = df['Candidate/Voter'].tolist()
    # print(f"Candidates: {candidates}")
    votes = []

    for voter in [col for col in df.columns if col != 'Candidate/Voter']:
        votings_dict = {}
        for vote, candidate in zip(df[voter].tolist(), candidates):
            votings_dict[candidate] = int(vote)
        votes.append(votings_dict)

    return candidates, votes

# Usage example
num_winners = 4  # Number of winners to retrieve
input_file = os.path.join(PROJECT_PATH, 'input_template.xlsx')  # Replace with the actual file name

candidates, votes = excel_to_preferences(input_file)

df = pd.DataFrame(votes)

evaluator = condorcet.CondorcetEvaluator(candidates=candidates, votes=votes)
winners, rest_of_table = evaluator.get_n_winners(num_winners)

print(winners)
print(rest_of_table)
