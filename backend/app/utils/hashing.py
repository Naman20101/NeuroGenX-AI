import hashlib, pandas as pd

def hash_df_head(df: pd.DataFrame, n=100) -> str:
    s = df.head(n).to_csv(index=False).encode()
    return hashlib.sha256(s).hexdigest()[:16]