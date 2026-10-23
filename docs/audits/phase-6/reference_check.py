"""Independent stdlib design model; no application imports, no P6 implementation claim."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_EVEN
import argparse, html, json

def reference(case):
    kind=case["kind"];x=case["inputs"]
    if kind=="weight":return format((Decimal(x["percent"])/100).normalize(),"f")
    if kind=="money":return format(Decimal(x["value"]).quantize(Decimal("0.01"),rounding=ROUND_HALF_EVEN),",.2f")
    if kind=="quantity":return str(int(x["value"]))
    if kind=="small":return format(Decimal(x["value"]),"f")
    if kind=="ic_display":return format(Decimal(x["value"]).quantize(Decimal("0.0001"),rounding=ROUND_HALF_EVEN),"f")
    if kind=="nullable":return {"text":"N/A" if x["value"] is None else str(x["value"]),"reason":x["reason"]}
    if kind=="percent_display":return format((Decimal(x["value"])*100).quantize(Decimal("0.0001"),rounding=ROUND_HALF_EVEN),"f")+"%"
    if kind=="canonical":return json.dumps(json.loads(x["raw"]),ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
    if kind=="array_order":return x["left"]==x["right"]
    if kind=="status_counts":return {"total":len(x["rows"]),"succeeded":sum(r["status"]=="SUCCEEDED" and r["verified"] for r in x["rows"]),"integrity_errors":sum(not r["verified"] for r in x["rows"])}
    if kind=="financial_view":return x["verified_balance"] if x["known"] and x["manifest_valid"] and x["reported_balance"]==x["verified_balance"] else None
    if kind=="idempotency":
        seen={};conflicts=0
        for key,value in x["calls"]:
            if key in seen:conflicts+=seen[key]!=value
            else:seen[key]=value
        return {"tasks":len(seen),"conflicts":conflicts}
    if kind=="lifecycle":
        state="QUEUED"
        for event in x["trace"]:
            if state in {"SUCCEEDED","FAILED","CANCELLED"}:continue
            if event=="START":state="RUNNING"
            elif event=="CANCEL_REQUEST":state="CANCELLED" if state=="QUEUED" else "CANCEL_REQUESTED"
            elif event=="SUCCESS":state="SUCCEEDED"
            elif event=="SAFE_CANCEL":state="CANCELLED"
            elif event=="FINANCIAL_UNKNOWN":state="FAILED"
        return state
    if kind=="artifact_membership":return x["manifest"].count(x["name"])==1
    if kind=="defaults_rollback":
        history=[dict(v) for v in x["history"]];history.append(dict(history[x["rollback_to"]]))
        return {"old_fee":history[0]["fee"],"active_fee":history[-1]["fee"],"revisions":len(history)}
    if kind=="nullable_equal":return type(x["left"]) is type(x["right"]) and x["left"]==x["right"]
    if kind=="formal_gate":return "APPROVAL_REQUIRED" if x["financial_approval"]=="NONE" else "REQUIRES_REAL_APPROVAL_VALIDATION"
    if kind=="family_trials":return x["initial"]+len({key for key,status in x["attempts"]})
    if kind=="escape":return html.escape(x["value"])
    if kind=="parent_identity":return x["expected_parent"]==x["actual_parent"] or x["mapping_proven"]
    if kind=="rerun":return x["explicit_submits"]
    raise AssertionError(kind)

def main():
    parser=argparse.ArgumentParser();parser.add_argument("output",type=Path);args=parser.parse_args()
    data=json.loads((Path(__file__).parent/"GOLDEN_CANDIDATES.json").read_bytes());records=[]
    for case in data["cases"]:
        got=reference(case);records.append({"id":case["id"],"expected":case["expected"],"actual":got,"pass":type(got) is type(case["expected"]) and got==case["expected"]})
    result={"executor":"Codex developer independent-stdlib design reference; not GPT Work independent review","scope":"Pre-implementation design model only, NOT P6 products or browser tests","groups":len(records),"passed":sum(r["pass"] for r in records),"failed":sum(not r["pass"] for r in records),"records":records}
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({k:result[k] for k in ("scope","groups","passed","failed")}));assert not result["failed"]
if __name__=="__main__":main()
