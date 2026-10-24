"""Independent stdlib design model; no application imports, no P6 implementation claim."""
from pathlib import Path
import argparse, html, json

MAX_DIGITS = 4096


class ReferenceNumberError(ValueError):
    """Explicit design-reference input refusal, never silent numeric rounding."""

    def __init__(self, code):
        super().__init__(code)
        self.code = code


def decimal_parts(text):
    if not isinstance(text, str):
        raise ReferenceNumberError("REFERENCE_NUMERIC_TYPE")
    if len(text) > MAX_DIGITS + 2:
        raise ReferenceNumberError("REFERENCE_NUMERIC_RANGE")
    sign = -1 if text.startswith("-") else 1
    body = text[1:] if text.startswith(("-", "+")) else text
    parts = body.split(".")
    if len(parts) > 2:
        raise ReferenceNumberError("REFERENCE_NUMERIC_SYNTAX")
    whole = parts[0]
    fraction = parts[1] if len(parts) == 2 else ""
    digits = whole + fraction
    if not digits or (len(parts) == 2 and not fraction) or any(c not in "0123456789" for c in digits):
        raise ReferenceNumberError("REFERENCE_NUMERIC_SYNTAX")
    if len(digits) > MAX_DIGITS:
        raise ReferenceNumberError("REFERENCE_NUMERIC_RANGE")
    return sign * int(digits), len(fraction)


def exact_text(coefficient, scale, *, trim=True):
    negative = coefficient < 0
    digits = str(abs(coefficient))
    if scale:
        digits = digits.zfill(scale + 1)
        whole, fraction = digits[:-scale], digits[-scale:]
        if trim:
            fraction = fraction.rstrip("0")
        result = whole + ("." + fraction if fraction else "")
    else:
        result = digits
    return ("-" if negative else "") + result


def rounded_units(coefficient, scale, places):
    if scale <= places:
        return coefficient * 10 ** (places - scale)
    denominator = 10 ** (scale - places)
    q, r = divmod(abs(coefficient), denominator)
    if 2 * r > denominator or (2 * r == denominator and q % 2):
        q += 1
    return -q if coefficient < 0 else q


def fixed_view(text, places, *, multiply=1, grouping=False):
    coefficient, scale = decimal_parts(text)
    value = exact_text(rounded_units(coefficient * multiply, scale, places), places, trim=False)
    if grouping:
        negative = value.startswith("-")
        whole, fraction = value.lstrip("-").split(".")
        chunks = [whole[max(0, i - 3):i] for i in range(len(whole), 0, -3)]
        value = ("-" if negative else "") + ",".join(reversed(chunks)) + "." + fraction
    return value


def reference(case):
    kind=case["kind"];x=case["inputs"]
    if kind=="weight":
        coefficient, scale = decimal_parts(x["percent"])
        return exact_text(coefficient, scale + 2)
    if kind=="money":return fixed_view(x["value"], 2, grouping=True)
    if kind=="quantity":
        coefficient, scale = decimal_parts(x["value"])
        if scale:
            raise ReferenceNumberError("REFERENCE_INTEGER_REQUIRED")
        return str(coefficient)
    if kind=="small":return exact_text(*decimal_parts(x["value"]))
    if kind=="ic_display":return fixed_view(x["value"], 4)
    if kind=="nullable":return {"text":"N/A" if x["value"] is None else str(x["value"]),"reason":x["reason"]}
    if kind=="percent_display":return fixed_view(x["value"], 4, multiply=100)+"%"
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
