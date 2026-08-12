from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from .icassp_statistics import ranking_metrics
from .optimization_protocol import ANALYTICAL, FAMILIES, UNIVERSAL_NEURAL


ROOT = Path(__file__).resolve().parent
OLD = ROOT / "outputs" / "optimization"
OUT = ROOT / "outputs" / "nested_optimization"
SEED = 20260801
WEIGHT_MODES = ("uniform", "inverse_fidelity", "fidelity_rank", "diversity", "combined", "trim_max")


def candidate_id(spec: dict) -> str:
    payload = json.dumps(spec, sort_keys=True, separators=(",", ":"))
    return "n_" + hashlib.sha256(payload.encode()).hexdigest()[:14]


def feature_family(name: str) -> str:
    return name.split("_")[0]


def formula_complexity(feature: str, weight_mode: str) -> int:
    score = 1
    if not feature.startswith("intensity_mean__"): score += 1
    if feature.startswith(("gradient", "laplacian", "local_energy")): score += 1
    if weight_mode != "uniform": score += 1
    return score


def rankdata_frame(values: pd.Series, ascending: bool = True) -> pd.Series:
    return values.rank(method="min", ascending=ascending)


def corrected_fidelity() -> tuple[pd.DataFrame, list[str], list[str]]:
    fidelity = pd.read_csv(OUT / "common_fidelity_per_case_development.csv")
    profile = fidelity.groupby(["dataset", "scale", "model"], as_index=False).agg(
        n=("case", "nunique"), mae=("mae", "mean"), mse=("mse", "mean"),
        psnr=("psnr", "mean"), ssim=("ssim", "mean"), ncc=("ncc", "mean"))
    ranks = []
    for (_, _), group in profile.groupby(["dataset", "scale"]):
        g = group.copy()
        for metric, ascending in (("mae", True), ("mse", True), ("psnr", False),
                                  ("ssim", False), ("ncc", False)):
            g[f"{metric}_rank"] = rankdata_frame(g[metric], ascending)
        g["fidelity_rank_score"] = g[[f"{m}_rank" for m in ("mae","mse","psnr","ssim","ncc")]].mean(axis=1)
        ranks.append(g)
    profile = pd.concat(ranks, ignore_index=True)
    fast = profile[profile.dataset.eq("fastmri")]
    overall = fast.groupby("model", as_index=False).agg(
        mean_mae=("mae", "mean"), mean_psnr=("psnr", "mean"), mean_ssim=("ssim", "mean"),
        mean_ncc=("ncc", "mean"), corrected_rank_score=("fidelity_rank_score", "mean"))
    overall["corrected_rank"] = rankdata_frame(overall.corrected_rank_score, True).astype(int)
    old = pd.read_csv(OLD / "development_fidelity_per_case.csv")
    old = old[(old.dataset.eq("fastmri")) & (~old.model.isin(ANALYTICAL))]
    old = old.groupby("model", as_index=False).mae.mean().sort_values("mae")
    old["original_unfair_rank"] = np.arange(1, len(old)+1)
    overall = overall.merge(old[["model","original_unfair_rank"]], on="model", how="left")
    overall["rank_change"] = overall.original_unfair_rank - overall.corrected_rank
    profile = profile.merge(overall[["model","corrected_rank","original_unfair_rank","rank_change"]], on="model", how="left")
    profile.to_csv(OUT / "corrected_reconstruction_fidelity.csv", index=False)

    neural = overall[overall.model.isin(UNIVERSAL_NEURAL)].sort_values("corrected_rank")
    peer_bank, family_counts = [], {}
    for model in neural.model:
        family = FAMILIES[model]
        if family_counts.get(family, 0) >= 2:
            continue
        peer_bank.append(model); family_counts[family] = family_counts.get(family, 0) + 1
        if len(peer_bank) == 6: break
    peer_bank += list(ANALYTICAL)
    cutoff = math.ceil(len(neural) / 2)
    main_targets = neural.head(cutoff).model.tolist()
    (OUT / "selected_public_model_bank.json").write_text(json.dumps(
        {"peer_bank": peer_bank, "main_targets": main_targets,
         "selection": "common-support fastMRI x2/x4/x6 fidelity rank; max two per family"}, indent=2), encoding="utf-8")
    return overall, peer_bank, main_targets


def candidate_subsets(bank: list[str], target: str) -> list[tuple[str, ...]]:
    peers = sorted(set(bank) - {target})
    subsets = []
    for size in (2, 3, 4, 5):
        if size <= len(peers): subsets.extend(itertools.combinations(peers, size))
    if tuple(peers) not in subsets: subsets.append(tuple(peers))
    return subsets


def static_weights(mode: str, members: tuple[str, ...], target: str, scale: int,
                   fidelity: pd.DataFrame, errors: pd.DataFrame) -> np.ndarray:
    if mode in {"uniform", "trim_max"}:
        return np.ones(len(members)) / len(members)
    f = fidelity[(fidelity.dataset.eq("fastmri")) & (fidelity.scale.eq(scale))].set_index("model")
    maes = np.asarray([f.loc[m, "mae"] for m in members])
    if mode == "inverse_fidelity": raw = 1 / np.maximum(maes, 1e-6)
    elif mode == "fidelity_rank": raw = np.exp(-.5 * stats.rankdata(maes))
    else:
        pivot = errors[(errors.dataset.eq("fastmri")) & (errors.scale.eq(scale))].pivot(index="case", columns="target_model", values="common_error")
        diversity = []
        for member in members:
            corr = stats.spearmanr(pivot[target], pivot[member]).statistic
            diversity.append(max(.05, 1-float(corr if np.isfinite(corr) else 0)))
        diversity = np.asarray(diversity)
        if mode == "diversity": raw = diversity
        else: raw = diversity / np.maximum(maes, 1e-6)
    return raw / raw.sum()


def score_from_matrix(matrix: np.ndarray, member_indices: list[int], weights: np.ndarray, mode: str) -> np.ndarray:
    values = matrix[:, member_indices]
    if mode == "trim_max" and values.shape[1] > 1:
        return (values.sum(axis=1) - values.max(axis=1)) / (values.shape[1]-1)
    return values @ weights


def public_search() -> None:
    fidelity_all, bank, main_targets = corrected_fidelity()
    fidelity = pd.read_csv(OUT / "corrected_reconstruction_fidelity.csv")
    errors = pd.read_csv(OUT / "common_errors_per_case_development.csv")
    pairs = pd.read_csv(OUT / "pair_features_per_case_development.csv")
    requested = {
        "intensity_mean__bank_union", "intensity_q90__bank_union", "intensity_top10__bank_union",
        "intensity_slice_max__bank_union", "intensity_slice_q90__bank_union", "intensity_top2__bank_union",
        "intensity_mean__input_derived", "intensity_q90__input_derived", "intensity_top10__input_derived",
        "intensity_mean__target_0.01", "intensity_q90__target_0.01", "intensity_top10__target_0.01",
        "relative_mean__bank_union", "relative_q90__bank_union",
        "gradient_mean__bank_union", "gradient_q90__bank_union",
        "laplacian_mean__bank_union", "local_energy_mean__bank_union",
    }
    features = [c for c in pairs.columns if c in requested]
    rows, registry = [], []
    for scale in (2,4,6):
        scale_pairs = pairs[(pairs.dataset.eq("fastmri")) & (pairs.scale.eq(scale))]
        scale_errors = errors[(errors.dataset.eq("fastmri")) & (errors.scale.eq(scale))]
        for target in UNIVERSAL_NEURAL:
            tp = scale_pairs[scale_pairs.target_model.eq(target)]
            cases = sorted(tp.case.unique())
            members_all = sorted(tp.member.unique())
            error_lookup = scale_errors[scale_errors.target_model.eq(target)].set_index("case").common_error
            y = np.asarray([error_lookup.loc[c] for c in cases])
            subsets = candidate_subsets(bank, target)
            for feature in features:
                matrix = tp.pivot(index="case", columns="member", values=feature).loc[cases, members_all].to_numpy()
                for members in subsets:
                    idx = [members_all.index(m) for m in members]
                    for mode in WEIGHT_MODES:
                        weights = static_weights(mode, members, target, scale, fidelity, errors)
                        score = score_from_matrix(matrix, idx, weights, mode)
                        spec = {"target_model": target, "scale": scale, "feature": feature,
                                "members": list(members), "weight_mode": mode,
                                "weights": [round(float(x), 8) for x in weights]}
                        cid = candidate_id(spec); metrics = ranking_metrics(y, score)
                        neural_count = sum(m not in ANALYTICAL for m in members)
                        cost = neural_count + .02 * (len(members)-neural_count)
                        record = {"candidate_id": cid, **spec, "members": ";".join(members),
                                  "weights": ";".join(map(str, spec["weights"])),
                                  "committee_size": len(members), "neural_member_count": neural_count,
                                  "cost_proxy": cost, "formula_complexity": formula_complexity(feature,mode),
                                  **metrics}
                        rows.append(record)
    result = pd.DataFrame(rows)
    # Stratified pruning preserves score, mask, structural-domain and cost families.
    keep = set()
    result["score_family"] = result.feature.map(feature_family)
    for _, group in result.groupby(["target_model","scale","score_family"]):
        keep.update(group.nsmallest(5, "normalized_aurc").candidate_id)
        keep.update(group.sort_values(["neural_member_count","normalized_aurc"]).head(3).candidate_id)
    result["selected_for_nested"] = result.candidate_id.isin(keep)
    result.to_csv(OUT / "score_committee_interaction_results.csv", index=False)
    registry = result[["candidate_id","target_model","scale","feature","members","weight_mode","weights",
                       "committee_size","neural_member_count","cost_proxy","formula_complexity",
                       "selected_for_nested","normalized_aurc","case_spearman","rrr_50"]].copy()
    registry["stage"] = "public_screening"
    registry["outer_evaluation_status"] = "not_opened"
    registry.to_csv(OUT / "candidate_registry.csv", index=False)
    print(f"public interactions={len(result)} retained={result.selected_for_nested.sum()} bank={bank} targets={main_targets}")


def candidate_scores(group: pd.DataFrame, candidates: pd.DataFrame) -> dict[str, pd.Series]:
    cases = sorted(group.case.unique()); members_all = sorted(group.member.unique())
    cache = {}
    result = {}
    for row in candidates.itertuples(index=False):
        key = row.feature
        if key not in cache:
            cache[key] = group.pivot(index="case", columns="member", values=key).loc[cases,members_all].to_numpy()
        members = tuple(row.members.split(";")); idx = [members_all.index(m) for m in members]
        weights = np.asarray([float(x) for x in row.weights.split(";")])
        result[row.candidate_id] = pd.Series(score_from_matrix(cache[key],idx,weights,row.weight_mode), index=cases)
    return result


def empirical_cdf(train: np.ndarray, test: np.ndarray) -> np.ndarray:
    ordered = np.sort(train)
    return np.searchsorted(ordered, test, side="right") / max(len(ordered),1)


def nested_select() -> None:
    pairs = pd.read_csv(OUT / "pair_features_per_case_ningxia.csv")
    errors = pd.read_csv(OUT / "common_errors_per_case_ningxia.csv")
    registry = pd.read_csv(OUT / "candidate_registry.csv")
    retained = registry[registry.selected_for_nested.astype(str).str.lower().eq("true")]
    manifests, inner_rows, predictions = [], [], []
    folds = sorted(pairs.fold.unique())
    for scale in (2,4,6):
        for target in UNIVERSAL_NEURAL:
            g = pairs[(pairs.scale.eq(scale)) & (pairs.target_model.eq(target))]
            cands = retained[(retained.scale.eq(scale)) & (retained.target_model.eq(target))]
            score_lookup = candidate_scores(g, cands)
            e = errors[(errors.scale.eq(scale)) & (errors.target_model.eq(target))].set_index("case")
            fold_by_case = g.drop_duplicates("case").set_index("case").fold
            for outer in folds:
                inner_cases = sorted(fold_by_case[fold_by_case.ne(outer)].index)
                outer_cases = sorted(fold_by_case[fold_by_case.eq(outer)].index)
                summaries = []
                for cand in cands.itertuples(index=False):
                    scores = score_lookup[cand.candidate_id]
                    fold_values=[]
                    for inner_fold in folds:
                        if inner_fold == outer: continue
                        fc=[c for c in inner_cases if fold_by_case.loc[c]==inner_fold]
                        if len(fc) < 2: continue
                        fold_values.append(ranking_metrics(e.loc[fc].common_error.to_numpy(),scores.loc[fc].to_numpy())["normalized_aurc"])
                    pooled = ranking_metrics(e.loc[inner_cases].common_error.to_numpy(), scores.loc[inner_cases].to_numpy())
                    finite=np.asarray([v for v in fold_values if np.isfinite(v)])
                    summaries.append({"outer_fold":outer,"scale":scale,"target_model":target,
                                      "candidate_id":cand.candidate_id,"mean_inner_nAURC":float(np.mean(finite)) if finite.size else pooled["normalized_aurc"],
                                      "worst_inner_nAURC":float(np.max(finite)) if finite.size else pooled["normalized_aurc"],
                                      "std_inner_nAURC":float(np.std(finite)) if finite.size else 0.0,
                                      "se_inner_nAURC":float(np.std(finite,ddof=1)/np.sqrt(len(finite))) if finite.size>1 else 0.0,
                                      "pooled_inner_nAURC":pooled["normalized_aurc"],"pooled_inner_rho":pooled["case_spearman"],
                                      "neural_member_count":cand.neural_member_count,"cost_proxy":cand.cost_proxy,
                                      "committee_size":cand.committee_size,"formula_complexity":cand.formula_complexity})
                summary=pd.DataFrame(summaries)
                for metric,weight in (("mean_inner_nAURC",1.),("worst_inner_nAURC",.5),("std_inner_nAURC",.25),("cost_proxy",.1)):
                    summary[f"rank_{metric}"]=summary[metric].rank(method="min")
                    summary["selection_J"] = summary.get("selection_J",0) + weight*summary[f"rank_{metric}"]
                best=summary.loc[summary.mean_inner_nAURC.idxmin()]
                threshold=best.mean_inner_nAURC+best.se_inner_nAURC
                eligible=summary[summary.mean_inner_nAURC<=threshold+1e-12]
                chosen=eligible.sort_values(["neural_member_count","cost_proxy","committee_size","formula_complexity","selection_J"]).iloc[0]
                low_pool=summary[(summary.committee_size<=3)&(summary.neural_member_count<=2)]
                low_best=low_pool.loc[low_pool.mean_inner_nAURC.idxmin()]
                low_threshold=low_best.mean_inner_nAURC+low_best.se_inner_nAURC
                low_eligible=low_pool[low_pool.mean_inner_nAURC<=low_threshold+1e-12]
                low_chosen=low_eligible.sort_values(["neural_member_count","cost_proxy","committee_size","formula_complexity","selection_J"]).iloc[0]
                summary["within_one_se"] = summary.candidate_id.isin(eligible.candidate_id)
                summary["selected_main"] = summary.candidate_id.eq(chosen.candidate_id)
                summary["selected_low_cost"] = summary.candidate_id.eq(low_chosen.candidate_id)
                inner_rows.extend(summary.to_dict("records"))
                for role, selected, role_threshold in (("nested_triage",chosen,threshold),("nested_low_cost",low_chosen,low_threshold)):
                    cand=cands[cands.candidate_id.eq(selected.candidate_id)].iloc[0]
                    manifests.append({"role":role,"outer_fold":outer,"scale":scale,"target_model":target,"candidate_id":selected.candidate_id,
                                      "feature":cand.feature,"members":cand.members,"weight_mode":cand.weight_mode,"weights":cand.weights,
                                      "inner_case_count":len(inner_cases),"outer_case_count":len(outer_cases),
                                      "one_se_threshold":role_threshold,"selected_mean_inner_nAURC":selected.mean_inner_nAURC,
                                      "selection_used_outer_labels":False})
                    raw=score_lookup[selected.candidate_id]
                    calibrated=empirical_cdf(raw.loc[inner_cases].to_numpy(),raw.loc[outer_cases].to_numpy())
                    for case,cal in zip(outer_cases,calibrated):
                        predictions.append({"method":role,"outer_fold":outer,"scale":scale,"case":case,"target_model":target,
                                            "candidate_id":selected.candidate_id,"raw_score":raw.loc[case],"triage_score":cal,
                                            "common_error":e.loc[case,"common_error"]})
    pd.DataFrame(manifests).to_csv(OUT / "ningxia_nested_selection_manifest.csv",index=False)
    pd.DataFrame(inner_rows).to_csv(OUT / "ningxia_inner_selection_results.csv",index=False)
    pd.DataFrame(predictions).to_csv(OUT / "ningxia_nested_predictions.csv",index=False)
    summarize_outer(pd.DataFrame(predictions))


def summarize_outer(predictions: pd.DataFrame) -> None:
    rows=[]
    for (method,scale,target),g in predictions.groupby(["method","scale","target_model"]):
        rows.append({"method":method,"scale":scale,"target_model":target,"n":len(g),
                     **ranking_metrics(g.common_error.to_numpy(),g.triage_score.to_numpy())})
    outer=pd.DataFrame(rows); outer.to_csv(OUT/"ningxia_outer_fold_results.csv",index=False)
    outer.to_csv(OUT/"nested_finalist_results.csv",index=False)


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--stage",choices=("public","nested"),required=True)
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    public_search() if args.stage=="public" else nested_select()


if __name__ == "__main__":
    main()
