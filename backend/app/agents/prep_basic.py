from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline

class PrepBasic:
    name="prep_basic"; version="0.1"
    def run(self, ctx):
        df = ctx["df"]
        target = ctx["target"]
        X = df.drop(columns=[target])
        y = df[target].astype(int)  # expects 0/1; extend for multiclass later
        num_cols = [c for c in X.columns if X[c].dtype.kind in "fc"]
        cat_cols = [c for c in X.columns if X[c].dtype.kind not in "fc"]

        pre = ColumnTransformer([
            ("num", StandardScaler(with_mean=False), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
        ])
        from sklearn.linear_model import LogisticRegression
        base = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])

        ctx["X"], ctx["y"], ctx["pipeline_template"] = X, y, base
        return ctx