import pandas as pd
import math
import pickle
from collections import defaultdict, Counter
# -------------------------------
# CONFIG
# -------------------------------
N_GRAM = 3        # 3-gram Markov model
MODEL_PATH = "markov_password_model.pkl"
DATASET_PATH = "/data.csv"   # path of uploaded dataset
class MarkovPasswordModel:
    def __init__(self, n):
        self.n = n
        self.transitions = defaultdict(Counter)
        self.totals = defaultdict(int)

    def train(self, passwords):
        for pwd in passwords:
            pwd = f"<{'^' * (self.n - 1)}>{pwd}<$>"
            for i in range(len(pwd) - self.n):
                context = pwd[i:i + self.n - 1]
                next_char = pwd[i + self.n - 1]
                self.transitions[context][next_char] += 1
                self.totals[context] += 1

    def probability(self, password):
        pwd = f"<{'^' * (self.n - 1)}>{password}<$>"
        log_prob = 0.0
        unseen_penalty = math.log(1e-6)

        for i in range(len(pwd) - self.n):
            context = pwd[i:i + self.n - 1]
            next_char = pwd[i + self.n - 1]

            if context in self.transitions and self.transitions[context][next_char] > 0:
                prob = self.transitions[context][next_char] / self.totals[context]
                log_prob += math.log(prob)
            else:
                log_prob += unseen_penalty

        return log_prob
df = pd.read_csv(
    DATASET_PATH,
    engine="python",
    on_bad_lines="skip",
    encoding="utf-8",
)
# Make sure column name is correct
passwords = df["password"].astype(str).tolist()

print("Total passwords:", len(passwords))

# Train model
model = MarkovPasswordModel(N_GRAM)
model.train(passwords)

print("Training completed")
'''
# Save model
with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

print("Model saved as", MODEL_PATH)
'''