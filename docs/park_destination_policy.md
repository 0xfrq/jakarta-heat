# AC-01/AC-02: candidate destination and permission policy proposal

Primary claim scope proposed for the coordinator: **modeled network distance to
OSM-mapped candidate park polygons**, using the 2026-11-19 OSM inventory with
2024 demographic/environmental patterns. No claim of verified citywide public
opening, 2024 access, actual cooling refuge suitability, walkable straight
connectors, or better health outcomes is made by the Agent2 remediation outputs.
Unknown tags remain uncertainty. Positive-only filtering is a sparse-destination
coverage stress scenario, not measured truth.

`park_access_evidence.csv` covers every one of the 1,015 preserved candidates,
retains the complete archived raw tag JSON, source snapshot and relevant
operator/opening/entrance/fee/permission fields. Evidence hierarchy:

1. Dated official/operator/field public-opening evidence **and matched physical
   identity/entrance** may support a verified destination.
2. Positive OSM access/foot is an unverified assertion.
3. Unknown OSM access is unknown; hours/conditional restrictions are separate.
4. Explicit restriction excludes a destination absent a documented override.

Every current `public_access_verified` and `entrance_verified` is false. The
verified-entrance GPKG intentionally contains an empty, typed Point layer; park
representative points are never fabricated as entrances. Conditional tags can
coexist with positive access; therefore the hierarchical evidence-state counts
(980 unknown,28 conditional,7 positive) differ from simple access-tag counts
(1005 unknown,9 yes,1 permissive). Both retain the underlying tags.

The auditor's initial top20 are all reviewed or explicitly unresolved. They
cover 91/254 audited top-M4 origins (35.8%). Four primary municipal context leads
were inspected/archived; they establish limited name/location/planning context,
not exact polygon boundaries, current gates, hours, permission or physical
opening. Source URLs, retrieval status, document publication date if actually
known, retrieval UTC and hashes are in `park_official_evidence_sources.json`.
An undated page is not assigned an invented publication date. Unnamed and weak
matches remain unresolved. No messages or field inquiries were sent.

`park_alternative_destinations.csv` gives the two nearest **distinct** candidate
parks per routable origin on the full fixed-node graph. The first distance is
checked against every saved full-graph baseline route; 2,526 origins have a
second candidate. Flags identify initial top20 winners, origins within50 m of
500/1000 m thresholds, and baseline ranks220–290 around the top-decile cutoff.
These alternatives are network proxies with unverified connectors, not confirmed
public substitutes. This supports targeted next evidence collection without
assuming that deletion of unknown parks is an accuracy improvement.

`walking_permission_manifest.json` states the conservative scenario precedence:
foot=no/private forbids; access=no/private forbids unless explicit foot
yes/designated/permissive; conditional cases and barrier-only nodes remain
unresolved. It retains all original snap nodes and removes edges incident on or
matching explicitly forbidden source nodes; direct connectors touching such
nodes are excluded. It never adds links or resnaps across a restriction.
Permission evidence is source-tag evidence, not verified closure. Unknown
physical crossings, fences/water, opening hours, one-way-foot and turn rules
remain limitations. This scenario is not silently promoted to the baseline.

`connector_validation.csv/.gpkg` records all origin/park connectors, node IDs,
source conflicts, blank permission overrides, review flags and unresolved
physical status. 167 origins and78 park connectors conflict with explicit OSM
node restrictions. The conservative routed result uses none of those forbidden
origin connectors or destinations. All66 far-snap origins and every top-M4
origin are included in the screen; physical/entrance inspection remains pending.
Nearest-edge resnapping without a validated legal connector was not adopted.
The disputed-connector map is a tag-screen map, not a legal crossing map.

Route-missing remains226 in the unchanged baseline and407 in the conservative
scenario. All original226 lie in graph components without candidate park nodes;
full-study graph extent recovers none. This is not proof of actual no access.
Conservative node/connector top-M4 fixed-set Jaccard is.895582; positive-only is
.421348. Top5/10/20 budgets, cap saturation, missingness and exact changed grids
are exported after demographic correction. Inventory has not changed because no
new public-opening evidence warrants it.

Approval still required: primary candidate/public construct; conditional
permissions and foot overrides; acceptable connector/entrance evidence; scenario
envelope; mixed-period scope. Agent3 must integrate these fields/scenarios into
DM-02/MD-03/EL-01/UI-01 before final claims. AC-01/AC-02 remain PARTIAL rather
than using a passing routing test as physical-access certification.
