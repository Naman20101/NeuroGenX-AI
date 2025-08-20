import optuna
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

class SearchOptuna:
    name="search_optuna"; version="0.1"
    def run(self, ctx):
        X, y = ctx["X"], ctx["y"]
        pre_clf: Pipeline = ctx["pipeline_template"]

        def objective(trial):
            C = trial.suggest_float("C", 1e-3, 1e2, log=True)
            clf = LogisticRegression(max_iter=1000, C=C, n_jobs=-1)
            pipe = Pipeline([("pre", pre_clf.named_steps["pre"]), ("clf", clf)])
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            # Use cross_val_predict to get probs for auc metrics
            prob = cross_val_predict(pipe, X, y, cv=cv, method="predict_proba")[:,1]
            from sklearn.metrics import roc_auc_score
            return roc_auc_score(y, prob)

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=ctx.get("n_trials", 40))
        best_C = study.best_params["C"]

        best_clf = LogisticRegression(max_iter=1000, C=best_C, n_jobs=-1)
        best_pipe = Pipeline([("pre", pre_clf.named_steps["pre"]), ("clf", best_clf)])
        best_pipe.fit(X, y)

        ctx["fitted_pipeline"] = best_pipe
        ctx["search_summary"] = {"best_auc_cv": study.best_value, "best_params": study.best_params}
        return ctx