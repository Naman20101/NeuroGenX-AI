from __future__ import annotations
import random
from typing import Dict, Any, List, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

# Hyperparam spaces (small, Render-friendly)
def random_logreg() -> Dict[str, Any]:
    return {
        "C": 10 ** random.uniform(-2, 2),
        "penalty": random.choice(["l2"]),   # saga/l1 removed for simplicity
        "solver": "lbfgs",
        "max_iter": 1000
    }

def random_rf() -> Dict[str, Any]:
    return {
        "n_estimators": random.choice([100, 200]),
        "max_depth": random.choice([None, 6, 10]),
        "min_samples_split": random.choice([2, 4, 8]),
        "min_samples_leaf": random.choice([1, 2, 4]),
        "n_jobs": -1
    }

def random_gb() -> Dict[str, Any]:
    return {
        "n_estimators": random.choice([100, 150]),
        "learning_rate": random.choice([0.05, 0.1, 0.2]),
        "max_depth": random.choice([2, 3]),
        "subsample": random.choice([0.8, 1.0])
    }

def instantiate(name: str, params: Dict[str, Any]):
    if name == "logreg":
        return LogisticRegression(**params)
    if name == "rf":
        return RandomForestClassifier(**params)
    if name == "gb":
        return GradientBoostingClassifier(**params)
    raise ValueError(name)

FAMILIES = [
    ("logreg", random_logreg),
    ("rf", random_rf),
    ("gb", random_gb),
]

def mutate(name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    # tiny random tweak
    rp = dict(params)
    if name == "logreg":
        rp["C"] *= 10 ** random.uniform(-0.2, 0.2)
    elif name == "rf":
        rp["n_estimators"] = max(50, int(rp.get("n_estimators", 100) + random.choice([-50, 0, 50])))
    elif name == "gb":
        rp["learning_rate"] = max(0.01, rp.get("learning_rate", 0.1) * random.choice([0.8, 1.0, 1.2]))
    return rp

def initial_population(pop: int) -> List[Tuple[str, Dict[str, Any]]]:
    out = []
    for _ in range(pop):
        fam, gen = random.choice(FAMILIES)
        out.append((fam, gen()))
    return out

def evolve(pop: List[Tuple[str, Dict[str, Any]]], k_best: int = 3, pop_size: int = 6) -> List[Tuple[str, Dict[str, Any]]]:
    # Select top-k, mutate, refill randoms
    top = pop[:k_best]
    children = []
    for fam, params in top:
        children.append((fam, mutate(fam, params)))
    while len(top) + len(children) < pop_size:
        fam, gen = random.choice(FAMILIES)
        children.append((fam, gen()))
    return top + children
