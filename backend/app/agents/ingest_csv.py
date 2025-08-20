from app.utils.io import load_csv
from app.utils.hashing import hash_df_head

class IngestCSV:
    name="ingest_csv"; version="0.1"
    def run(self, ctx):
        df = load_csv(ctx["dataset_id"])
        ctx["df"] = df
        ctx["dataset_hash"] = hash_df_head(df)
        return ctx
