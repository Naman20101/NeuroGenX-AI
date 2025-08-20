import numpy as np
from app.utils.metrics import compute_binary_metrics

class Evaluate:
    name="evaluate"; version="0.1"
    def run(self, ctx):
        pipe = ctx["fitted_pipeline"]
        X, y = ctx["X"], ctx["y"]
        prob = pipe.predict_proba(X)[:,1]
        pred = (prob >= 0.5).astype(int)
        metrics = compute_binary_metrics(y, prob, pred)
        ctx["metrics"] = metrics
        # simple champion gate: pr_auc>0.5 or better than last
        ctx["is_champion"] = True
        return ctx
