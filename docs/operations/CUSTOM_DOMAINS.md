# Custom-domain setup

## www hostnames

| Type | Name | Value |
| --- | --- | --- |
| CNAME | www.autorite.org | custom-domains.chatgpt.site. |
| TXT | _openai-site-verification.www.autorite.org | `openai-site-verification=EDFEGdoKqiVW0PCm2UXXUkvBGXIujmR_gv_lkIAMtEs` |
| TXT | _cf-custom-hostname.www.autorite.org | `0a42ebf4-adf4-47e9-a1dc-e9676f83e768` |
| CNAME | www.autorite.net | custom-domains.chatgpt.site. |
| TXT | _openai-site-verification.www.autorite.net | `openai-site-verification=5GznjPpwDdvUNLrjCtTr0ZdJYOASYsvc1vtxoTUU7EA` |
| TXT | _cf-custom-hostname.www.autorite.net | `df786c1e-eebb-4db2-b1bd-10eb683e21ab` |

Both English sites are published and publicly accessible at `https://autorite.org` and `https://autorite.net`. On 2026-10-07, the Cloudflare DNS records were applied to both apex domains and their www hostnames. All four domain and SSL validations succeeded; provider states are recorded in `CUSTOM_DOMAIN_STATUS.json`. Previous Vercel routing records are preserved in `DNS_BEFORE_SITES.json` for rollback. Apex hosts use the returned A targets; www hosts use `custom-domains.chatgpt.site` with DNS-only routing. Unrelated records were preserved.

## autorite.org

| Type | Name | Value |
| --- | --- | --- |
| A | autorite.org | 162.159.143.30 |
| A | autorite.org | 172.66.3.26 |
| TXT | _openai-site-verification.autorite.org | `openai-site-verification=iCE477bdtDB8nqra7hZVE0vQJYmQbAk9Ep5OqJvBTsg` |
| TXT | _cf-custom-hostname.autorite.org | `b735f46f-81c2-41b1-bdc3-47d90d2c347d` |

## autorite.net

| Type | Name | Value |
| --- | --- | --- |
| A | autorite.net | 162.159.143.30 |
| A | autorite.net | 172.66.3.26 |
| TXT | _openai-site-verification.autorite.net | `openai-site-verification=7BPJELrsjSteocbYZSctD8POdLTOsoUbvDIsVfPfi8Y` |
| TXT | _cf-custom-hostname.autorite.net | `64dbaa8b-c5bf-4360-8d55-a659c6416f92` |

`canonical/site-origins.json` now uses the verified HTTPS custom domains. Both sites were regenerated so canonical URLs and cross-site links use those domains. Their original Sites URLs remain available. Future updates must preserve these origins and the registered project IDs.
