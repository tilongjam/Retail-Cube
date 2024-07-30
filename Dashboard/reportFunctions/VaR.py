import numpy as np
import pandas as pd
import os


class VaR:
    def __init__(self, data_path) -> None:
        self.data_path = data_path
        self.var = {}
        self.pnl_vectors = {}

    def var_calc(self):
        for file in os.listdir(self.data_path):
            df = pd.read_csv(os.path.join(self.data_path, file))
            df = df[df['P&L Instrument'].str.strip()!="Total"]
            self.pnl_vectors[file.split(".")[0]] = np.array(df["Result"])
            pnl_vector = np.sort(np.array(df["Result"]))
            self.var[file.split(".")[0]] = np.percentile(pnl_vector, 1)
        return self.var


if __name__ == "__main__":

    main_path = (
        r"C:\Users\gduremanthi.ext\Documents\RetailCube Backend\Data\Report Data\VaR Data"
    )
    test = VaR(main_path)
    var = test.var_calc()
