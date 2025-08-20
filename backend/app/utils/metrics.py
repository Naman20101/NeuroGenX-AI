from sklearn.metrics import roc_auc_score, average_precision_score, f1_score

def compute_binary_metrics(y_true, y_prob, y_pred):
    out = {}
    out["auc"]    = float(roc_auc_score(y_true, y_prob))
    out["pr_auc"] = float(average_precision_score(y_true, y_prob))
    out["f1"]     = float(f1_score(y_true, y_pred))
    return out