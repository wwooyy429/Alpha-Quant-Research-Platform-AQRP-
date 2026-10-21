# Phase 1 data validation correction

Patch 0.1.1 enforces existing DATA-001/002/004/006/011 and QA-002 requirements. No public schema, query signature, frozen contract, Golden answer, dependency lock, factor, portfolio, execution or account implementation changes.

- Volume accepts share/lot source dimensions; amount accepts currency/thousand_currency. Known units are checked even when the normalized value is missing. Normalized shares must follow SYNTHETIC_V1.share_unit. Legal lot and currency conversions remain valid.
- Every known OHLC pair must respect low <= open/close <= high and low <= high. A missing value stays MISSING only if all known values remain consistent.
- Corporate actions require an unambiguous ex-date calendar session in the security market. effective_at is interpreted in that calendar's IANA zone, not its UTC date or the feed's timezone. It must fall on ex_date, no later than ex-session close; pre-open on that date is valid. Missing/ambiguous ex-sessions fail closed. Overnight company-action conventions whose close falls on another local date are explicitly unsupported in this synthetic profile. Ordinary overnight bars are not changed. Future/late revisions remain gated by available_at. No pay-date cash accounting is added.

CI now uploads .coverage and the installed project wheel. upload-selection.json enumerates exact successful-run raw bytes, excluding itself; pinned gitleaks and pip bootstrap binaries are explicitly omitted. Failed runs retain available logs/environment through always-upload; an early failure need not produce a successful selection receipt. Historical ZIP omissions cannot be repaired by generating replacement bytes.
