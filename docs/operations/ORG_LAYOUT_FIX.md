# Knowledge-site layout correction — 2026-10-07

Text-only inner-page headers inherited a two-column hero and reserved an empty Cycle column. The shared 800px breakpoint also switched narrower desktop browser panels into the phone layout.

The org-specific stylesheet now gives text-only headers the full available width, widens the desktop content surface to 1440px, and retains the two-column research layout above 640px. Phone layouts still stack the content. Header navigation wraps separately where necessary. Content-hashed stylesheet URLs prevent an older cached stylesheet from hiding the correction. The laboratory output is unchanged.

Browser verification: at 1440px and 768px, the homepage hero and research cards have two columns; at 390px they have one. No horizontal overflow was observed at these sizes. At 1440px, the Questions header and its text column both span 1296px. The default 1015px viewport also shows the full-width inner-page header. All 267 existing asset/source/page link checks pass.
