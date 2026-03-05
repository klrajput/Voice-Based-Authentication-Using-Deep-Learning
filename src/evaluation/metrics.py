import pandas as pd

LOG_FILE = "data/logs/auth_log.csv"

import matplotlib.pyplot as plt




def compute_metrics():

    df = pd.read_csv(LOG_FILE)

    threshold = 0.65

    FAR = len(df[(df["score"] > threshold) & (df["result"] == "reject")]) / len(df)

    FRR = len(df[(df["score"] <= threshold) & (df["result"] == "accept")]) / len(df)

    print("False Accept Rate:", FAR)

    print("False Reject Rate:", FRR)

    plt.scatter(df["score"], df["result"])

    plt.xlabel("Similarity Score")
    plt.ylabel("Decision")

    plt.show()