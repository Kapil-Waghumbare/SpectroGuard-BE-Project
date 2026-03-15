import pandas as pd
import math
from collections import defaultdict, Counter

# CONFIG


N_GRAM = 4  # higher-order Markov model
DATASET_PATH = "/home/kapil/Desktop/Kapil/SPECTROGUARD/data.csv"  # FIXED PATH

# MODEL

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

    def score(self, password):
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

        # IMPORTANT FIX:
        # lower probability = stronger password
        strength_score = min(100, max(0, int(-log_prob)))
        return strength_score, log_prob


# LOAD DATASET

df = pd.read_csv(
    DATASET_PATH,
    engine="python",
    on_bad_lines="skip",
    encoding="utf-8"
)

passwords = df["password"].astype(str).tolist()
print("Passwords loaded:", len(passwords))

# TRAIN MODEL

model = MarkovPasswordModel(N_GRAM)
model.train(passwords)
print("Model trained using", N_GRAM, "-gram Markov model")


# TEST PASSWORDS

while True:
    pwd = input("\nEnter password to test (exit to quit): ")
    if pwd.lower() == "exit":
        break

    score, log_prob = model.score(pwd)

    print("Log Probability:", round(log_prob, 2))
    print("Strength Score:", score, "/ 100")

    if score < 30:
        print("Verdict: Very Weak (easily guessable)")
    elif score < 60:
        print("Verdict: Weak")
    elif score < 80:
        print("Verdict: Strong")
    else:
        print("Verdict: Very Strong (highly unpredictable)")
