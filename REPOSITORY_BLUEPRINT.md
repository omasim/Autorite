# Repository Blueprint
```text
autorite-research/
├── baseline/v0.1/
├── canonical/
├── cycles/cycle-01/
├── research/{RP002A,RP003,RP004,RP005A}/
├── graph/{questions,claims,assumptions,tests,results,decisions,sources}/
├── legacy/damx/
├── protocols/
├── publications/
├── apps/{org,net}/
├── packages/{research-schema,content,ui-foundation}/
├── scripts/
├── docs/{decisions,operations}/
└── .github/{ISSUE_TEMPLATE,workflows}
```

`main` is canonical. Use short-lived `research/*`, `legacy/*`, `site/org-*`, `site/net-*`, `infra/*`, `correction/*` branches. Avoid long-lived `develop`.

Release anchors: `baseline-v0.1`, `cycle-01-checkpoint-a`, `cycle-01-close`.
