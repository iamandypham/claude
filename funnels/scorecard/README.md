# Revenue Leak Scorecard on GHL

- `scorecard-live.html`: the page pasted into one Custom Code element on the GHL funnel step `/scorecard` (businessgrowr.com). Built from the draft 5 prototype with `build_live.py`.
- Lead POST: `https://businessgrowr.app.n8n.cloud/webhook/bg-scorecard-ghl` (n8n workflow 4WaO3TM95EeZePXd, source in `n8n-scorecard-workflow.sdk.js`, Discord and notify hooks left as placeholders here).
- Tests: `node test_live.js scorecard-live.html` (83 checks, every outside request intercepted) and `node test_booked.js scorecard-live.html`.
- Real leads are held in n8n (`LIVE = false` in "Map Scorecard") until Andy's go. Test leads (`@example.com`, `zz…`, `?bgtest=1`) reach GHL with no phone and tags `scorecard-test`, `dialer-off`.
