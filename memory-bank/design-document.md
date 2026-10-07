# PsychTalk Hub — Product Design Document

Current stage / 当前阶段 (7 October 2026): verified release **06f98e2** is Live; local checks, exact-commit CI, current online core checks and authorized backup/isolated restore passed. Management video and complete production management acceptance remain pending, so this is not full MVP acceptance. Product and API rules below are unchanged. Actual evidence: [progress](progress.md), [architecture](architecture.md), [delivery](../DELIVERY.md).

Version: MVP v0.2 | Date: 3 October 2026 | Status: Design specification; implementation not yet verified

[中文版](design-document.zh-CN.md) · [Technology stack](tech-stack.md)

This document is the product requirements and interaction-design reference. Its Chinese counterpart specifies the same behaviour. Technical choices and deployment guidance are maintained in the technology-stack document.

## 1. Product overview and scope

PsychTalk Hub is a learning-resource platform for psychology talks. Organisers curate relevant papers and articles; visitors explore reading before an upcoming talk and continue learning after a past talk.

The product hypothesis is that a shared activity page makes reading easier to find and reduces repeated resource-sharing work. This remains unvalidated. The product is an independent portfolio prototype inspired by public information about Conn8cting, with no official affiliation.

| Audience | Main task | Intended outcome |
| --- | --- | --- |
| Visitor | Open a talk and explore its reading | Find relevant resources without creating an account |
| Organiser | Add and maintain reading for a talk | Publish a useful resource page and share its URL |
| Portfolio reviewer | Browse the public demo and watch the admin video | Understand the product and its management workflow |

The three-day MVP includes two public pages, Django Admin, DOI import, manual resources, title search, and basic error handling. It excludes registration, booking links, payments, chat, AI recommendations, multi-tenancy, a global research search, and native mobile apps.

The 18–24-hour budget targets a reviewable version: prioritise the complete core workflow, key tests, GitHub and reproducible setup. Unfinished online acceptance or video work must remain explicit follow-up items. Full MVP completion still requires all acceptance criteria below; permissions, transactions and duplicate protection cannot be skipped.

All product UI and demonstration content use English. This document and its Chinese counterpart specify the same behaviour.

## 2. Information architecture

| Surface | Proposed route | Contents and access |
| --- | --- | --- |
| Home | `/` | Upcoming and past talks; public |
| Talk details | `/events/{id}` | Talk information and related reading; public |
| Administration | `/admin/` | Login, event/resource maintenance and DOI import; authorised administrators only |

There is no separate resource detail page. Reading links lead to the original external website. The public navigation contains the product name linking to Home; it does not advertise administrator credentials or a login action.

The public demo supports visitor browsing. A short video shows event creation, DOI preview, confirmation and duplicate handling. Administrator credentials remain private.

## 3. Visual and accessibility direction

The interface should feel like a warm learning community: calm, readable and welcoming, with resource information taking priority over decoration.

| Token | Design value |
| --- | --- |
| Page background | Warm white, `#FAF8F4` |
| Card background | White, `#FFFFFF` |
| Primary colour | Deep green, `#245448` |
| Main text | `#23332D` |
| Secondary text | `#56645D` |
| Border | `#DDDCD4` |
| Error text | `#A32626`, accompanied by an explanatory message |
| Font | System sans-serif stack; no external font dependency |
| Type sizes | Body 16 px; section title 24 px; page title 36 px desktop / 28 px mobile |
| Spacing | 8 px base; use 8, 16, 24 and 32 px increments |
| Content width | Maximum 1080 px; horizontal padding 24 px desktop / 16 px mobile |
| Cards and controls | Card radius 12 px; input/button radius 8 px; controls at least 44 px high |

Below 768 px, talk cards use one column; at 768 px and above, they use two columns. Resource cards always use one column. Long titles and links wrap without horizontal scrolling.

Use visible keyboard focus, explicit input labels, semantic headings and text explanations for errors. Do not rely on colour alone to convey status. Check text contrast before implementation is accepted. No cover images, icon pack or complex animation is required. Django Admin retains its standard styling; custom import screens use its existing forms and messages.

## 4. Home page

### Layout and content

The header shows **PsychTalk Hub**. The introduction reads **Keep learning beyond the talk.**, followed by **Explore reading for upcoming and past psychology talks.**

Show `Upcoming talks` first and `Past talks` second. Each card contains the talk title, topic, London-local start time, speaker, related-resource count, and an `Explore resources` action.

- An event is upcoming when its start instant is later than the current instant; otherwise it is past. No end-time field is introduced.
- Upcoming talks sort by start time ascending; past talks sort by start time descending. Equal start times use event ID ascending.
- Use `Europe/London` for display, including the applicable GMT/BST label. The admin form clearly states its time zone.
- Both groups remain visible when empty, with a short message. An event with zero resources still has a working detail page.
- Refreshing a detail URL or using browser Back must work normally.

### Low-fidelity wireframe 1

```text
+------------------------------------------------------+
| PsychTalk Hub                                        |
+------------------------------------------------------+
| Keep learning beyond the talk.                       |
| Explore reading for upcoming and past psychology     |
| talks.                                               |
|                                                      |
| Upcoming talks                                       |
| +-----------------------+ +------------------------+ |
| | Example event         | | Example event          | |
| | Title / topic         | | Title / topic          | |
| | Date, time, GMT/BST   | | Date, time, GMT/BST    | |
| | Speaker / 3 resources | | Speaker / 3 resources  | |
| | [Explore resources]   | | [Explore resources]    | |
| +-----------------------+ +------------------------+ |
|                                                      |
| Past talks                                           |
| +--------------------------------------------------+ |
| | Example event / title / date / speaker            | |
| | 3 resources                     [Explore resources]| |
| +--------------------------------------------------+ |
| Independent portfolio prototype · Example events     |
+------------------------------------------------------+
```

The wireframe illustrates hierarchy; every talk card uses the same structure in the final grid.

## 5. Talk details and reading

Show `Back to talks`, an `Upcoming` or `Past` label, title, topic, time, speaker and description. Place the `Related reading` section immediately below the talk information.

The search input has the visible label `Search resources` and placeholder `Search by title`. Filtering is case-insensitive, uses the trimmed query as a title substring, and affects only resources linked to this event. Update results as the user types; clearing the query restores the full list and administrator-defined order. No server-wide or Crossref search is exposed to visitors.

Each resource card displays:

1. Resource type: `Research paper` or `Article / web resource`.
2. Title, authors and publication year.
3. `Why this reading?` and the organiser's recommendation.
4. `Read original`, opening the original URL in a new tab with that behaviour indicated in its accessible label.

Missing authors display `Author not provided`; a missing year displays `Year not provided`. Display recommendations as written by the organiser; do not generate scientific conclusions. If no recommendation is supplied, omit that block. The platform links to sources and does not host paper full texts or guarantee publisher access.

### Low-fidelity wireframe 2

```text
+------------------------------------------------------+
| PsychTalk Hub                                        |
| < Back to talks                                      |
|                                                      |
| Example event                           [Upcoming]   |
| Talk title                                           |
| Topic · Date, time, GMT/BST · Speaker                 |
| Short description                                    |
|                                                      |
| Related reading                                      |
| Search resources                                     |
| [Search by title                              ]      |
| 3 resources                                          |
| +--------------------------------------------------+ |
| | Research paper                                   | |
| | Resource title                                   | |
| | Author names · Publication year                  | |
| | Why this reading?                                | |
| | Organiser's short recommendation                 | |
| | [Read original]                                  | |
| +--------------------------------------------------+ |
| More resource cards                                  |
+------------------------------------------------------+
```

## 6. Administration and publishing

### Event maintenance

Administrators create and edit title, description, topic, start time and speaker using Django Admin. Title and start time are required. Saved events are immediately public, including events with no reading yet; no draft or approval stage exists. Show a link to the public page after saving.

Description, topic and speaker are optional strings; omit their display when empty. Deleting an event requires confirmation: **Delete this talk and its reading links? Shared resources will be kept.** Delete the event and its associations, retaining every Resource. This applies to single and bulk event deletion. Shared Resource deletion is disabled, including bulk actions and direct deletion URLs.

### DOI import

Provide a small two-step import form within Django Admin, with the target event always visible:

1. Enter a DOI and select `Fetch metadata`. Accept a bare DOI or a `https://doi.org/` link and normalise it before lookup. Check saved resources first; an existing DOI does not require another Crossref request.
2. For a new DOI, preview the title, authors, year and original URL obtained through the server-side Crossref integration, supplement missing fields and add a recommendation and numeric display order. For an existing DOI, display saved bibliographic information read-only and edit only the recommendation and order for this event. Shared metadata changes belong on the Resource edit page.
3. Select `Save to event`. The resource and its event association are persisted together; successful saving makes the association public immediately.
4. Display `Resource added to this talk.` and a link to the public page.

Fetching and previewing do not create or modify Resource or EventResource records; saving protected session state is allowed. Disable the relevant submit control while a request is pending and show `Fetching…` or `Saving…`. Do not overwrite user-entered values after an unsuccessful save. Cancelling the preview invalidates it and returns to the event without changing resources or associations.

Each preview has an independent random identifier in a Django database-backed session, bound to the administrator and target event. It expires 15 minutes after metadata is successfully fetched or an existing resource is loaded; edits and retries do not extend the deadline. Multiple tabs keep separate previews. Confirmation rechecks the session, model permissions, target, expiry and fields. While valid, repeated confirmation returns the existing result without changing its recommendation or order. Expired, cancelled or invalid previews cannot save; show the state defined below and offer a fresh lookup. If the event is deleted before confirmation, refuse saving and return to event administration.

### Manual resources and existing resources

`Add manually` requires a title and an HTTP(S) original URL. Authors and year are optional. Add the recommendation and numeric display order when linking it to an event. Administrators can also select an existing resource instead of importing it again.

Manual resources are not automatically merged by title or URL. Administrators can deliberately select an existing resource. The source is `manual`; imported resources retain `crossref` even after bibliographic edits.

Resource metadata is shared between events. Before saving an edit to an existing resource, display: **Changes to this resource will appear in every talk that uses it.** Recommendations and display orders belong to each event association and can be edited independently.

Remove an association through `Remove from this talk`, with the confirmation **Remove this reading from this talk? Other talks will keep it.** All writes, including import requests, require server-side administrator authorisation and Django model permissions. The MVP has no per-event ownership rules or multi-tenant permissions.

## 7. Content and data rules

| Entity | Responsibility |
| --- | --- |
| Event | Talk title, description, topic, start time, speaker, example flag and optional stable seed identifier |
| Resource | Shared title, authors, year, original URL, optional DOI, resource type, metadata source and optional stable seed identifier |
| EventResource | Event/resource relationship, optional recommendation and numeric display order |

- Store a normalised DOI once per resource; match an existing DOI before creating another resource.
- Enforce a unique event/resource association in the database. Repeated clicks or concurrent saves must not create duplicates.
- When a DOI already exists in another talk, reuse the resource without silently overwriting its metadata. When it is already linked to the target talk, show the existing association instead of creating another.
- Sort resources by display order ascending, then association ID ascending. Default display order is `0`; equal values preserve association creation order.
- Missing authors/year are allowed; a non-empty title and valid HTTP(S) original URL are required before saving.
- Imported metadata is bibliographic information, not an endorsement of research quality. Save only the fields needed for the cards; do not add automated summaries or import abstracts in the MVP.
- Every seeded demonstration event carries an `Example event` label. The public footer states: `Independent portfolio prototype. Not affiliated with Conn8cting.` Developers select and verify real papers and articles for two fictional talks, with at least three resources each. Show `Reading selections are illustrative; these talks are fictional.` on example-event details. Never invent paper titles, authors or DOIs.
- Use stable seed identifiers for events and resources without DOIs, and normalised DOIs for imported resources. Repeated seeding only fills missing records and associations; it never overwrites edits. On initial creation, set the upcoming event 30 days after the seed instant and the past event 7 days before it. Later imports never shift dates automatically; recheck the demo's upcoming/past mix when reviewing it.

### DOI and bibliographic conversion

- Trim surrounding whitespace and lowercase the DOI. Bare identifiers must start with `10.`, contain a 4–9-digit registrant followed by `/`, and have a non-empty suffix without whitespace. Preserve suffix punctuation; do not strip trailing punctuation heuristically.
- DOI links must use HTTPS and the exact host `doi.org`, with no credentials, explicit port, query or fragment. Decode the path once, then validate it as a bare DOI. Reject other hosts before any network call; encode the normalised DOI as one identifier in the fixed Crossref endpoint.
- Use the first non-empty title. Join each author's given and family names, or its organisation name when personal names are absent, in source order with `; ` separators. Missing authors remain an empty string.
- Select the first valid integer year from `published-print`, then `published-online`, then `issued`; valid years are 1–9999. Missing years remain null. Use Crossref's HTTP(S) URL; if it is absent or invalid, require administrator input before saving.
- Map `journal-article` and `proceedings-article` to `research_paper` / `Research paper`; other Crossref types map to `article` / `Article / web resource`. Manual entry allows either type. Metadata source is `crossref` or `manual`; no abstracts or generated summaries are stored.

### Public API contract

The authoritative field/type specification is in [Technology stack — public API contract](tech-stack.md#public-api-contract). The unpaginated list uses event objects; the detail includes the same fields plus ordered resources. IDs are integers, times are UTC ISO 8601, missing authors are empty strings, and missing years/DOIs are null. Error responses contain a JSON `detail` string, with 404 for missing events and 405 for unsupported methods. Visitors never receive session or preview identifiers.

## 8. User journeys

### Visitor journey

```mermaid
flowchart TD
    A[Open Home] --> B[Browse upcoming or past talks]
    B --> C[Explore resources]
    C --> D[Read talk details and related reading]
    D --> E{Search by title?}
    E -->|Yes| F[Filter this talk's resources]
    F --> G[Review resource and recommendation]
    E -->|No| G
    G --> H[Read original in a new tab]
```

### Administrator DOI journey

```mermaid
flowchart TD
    A[Log in to Django Admin] --> B[Create or select an event]
    B --> C[Enter and normalise DOI]
    C --> X{Resource already saved?}
    X -->|Yes| Y[Preview saved metadata read-only]
    Y --> G[Add recommendation and display order]
    X -->|No| N[Fetch Crossref metadata]
    N --> D{Lookup successful?}
    D -->|No| E[Explain error; retry or add manually]
    E --> C
    E --> M[Complete manual form]
    D -->|Yes| F[Preview and supplement metadata]
    F --> G
    G --> H[Confirm save]
    M --> H
    H --> I{Already linked to this event?}
    I -->|Yes| J[Show existing association]
    I -->|No| K[Save resource and association atomically]
    K --> L[View the public event page]
    J --> L
```

The journeys do not require visitor accounts. Saved changes become visible on the next successful page load; real-time updates are outside the MVP.

## 9. Loading, empty and failure states

| Context | English UI copy | Behaviour |
| --- | --- | --- |
| Loading a public page | `Loading talks…` / `Loading resources…` | Show a stable loading region; do not show an empty-state message yet |
| No upcoming talks | `No upcoming talks yet. Explore past talks below.` | Keep the past-talks section available |
| No past talks | `No past talks yet.` | Keep the upcoming-talks section available |
| No talks at all | `Talks will appear here when they are added.` | Display the message below the introduction |
| No linked resources | `Reading resources will be added here soon.` | Retain the event information; omit search until resources exist |
| No search results | `No resources match your search.` | Offer `Clear search` without changing the event |
| Event not found | `We couldn't find this talk.` | Offer `Back to talks` |
| Public request failed | `We couldn't load this page. Please try again.` | Offer `Retry`; do not report this as an empty list |
| Invalid DOI input | `Enter a valid DOI or DOI link.` | Keep the input; do not call Crossref or save a record |
| DOI not found | `No publication was found for this DOI.` | Allow input correction or `Add manually` |
| Lookup timed out / provider unavailable | `We couldn't fetch publication details. Please try again or add the resource manually.` | Keep the DOI; allow retry or manual entry; no automatic retry loop |
| Incomplete metadata | `Some details are missing. Review before saving.` | Missing authors/year are allowed; require title and original URL |
| Duplicate association | `This resource is already linked to this talk.` | Offer the existing record; create no duplicate |
| Expired / invalid / cancelled preview | `This preview is no longer valid. Fetch metadata again.` | Refuse saving; offer a new lookup |
| Event removed during import | `This talk is no longer available.` | Refuse saving; offer return to event administration |
| Save failed | `We couldn't save this resource. Please try again.` | Keep form values and ensure no partial association is committed |
| Unauthorised admin action | `You don't have permission to make this change.` | Reject writes; require a valid administrator session |

## 10. Delivery and acceptance

Use React + Vite, Django + Django REST Framework, PostgreSQL, Crossref REST API and GitHub Actions, with the API contract, version recommendations and deployment details defined in the [technology stack](tech-stack.md). Use Django Admin rather than implementing a React management dashboard. Public data reading and administrator-only writing remain separate capabilities.

Use independent Python 3.13 and PostgreSQL 17 development environments, preserving existing installations. Deployment uses one free Render Web Service and a free database in the same region, with no paid upgrades. Record cold starts, the database expiry date and backup limitations. Deploy verified commits manually; run migrations before Gunicorn at startup. Seed data and initialise the private administrator separately through a controlled local production connection. Missing account access or unavailable free capacity is an external blocker, not a reason to purchase a service.

| Day | Intended milestone |
| --- | --- |
| 1 | Models, Django Admin, read APIs, public React pages, example data, early dependency locks/CI/health check, minimal production assets and a deployment attempt |
| 2 | DOI preview/save, search, permissions, duplicate protection, failure handling and key automated tests |
| 3 | Reproducibility and deployment checks, mobile checks, README, bilingual documentation and video; publish a reviewable version with any remaining work explicitly listed |

Full MVP acceptance requires all of these scenarios; a three-day reviewable version must identify any unmet items:

- At least two example events have at least three resources each; the demo includes upcoming and past events.
- Upcoming/past grouping and order are correct, including the exact start-time boundary and London time display.
- Visitors can browse without logging in, open a direct event URL, refresh it and use browser Back.
- Search stays within the current event; case differences, surrounding spaces, clearing and no matches behave as specified.
- Valid DOI import supports preview, confirmation, cancellation and immediate publication; manual resources can also be added.
- A preview expires after 15 minutes, survives independent tab use, and cannot be saved by another session or for a changed target. Cancellation and expiry reject writes; repeated valid confirmation is idempotent.
- Duplicate DOI use reuses metadata, while repeated/concurrent association saves create only one link.
- Existing DOI metadata is read-only during import; manual entries are not automatically merged. Conversion follows the documented DOI, author, year, type and missing-URL rules.
- Invalid DOI, lookup failure, missing optional fields and unsuccessful saves produce the defined states without partial data.
- Resource ordering and per-event recommendations work independently; removing a link leaves other events intact.
- Confirmed event deletion removes only that event and its associations; shared-resource single, bulk and direct-URL deletion are blocked.
- API field types, nulls, ordering, JSON errors, 404 and 405 match the contract. Seeding twice preserves dates, stable identities and manual edits.
- Anonymous or non-administrator requests cannot perform writes; the demo does not expose administrator credentials.
- The pages work at 375 px and 1280 px widths, with wrapping, labelled inputs and visible keyboard focus.
- Backend tests run in CI; README covers setup, sample data, architecture and known limitations. The video demonstrates management operations.
- Free deployment migrates before starting, fails startup on migration failure, and preserves data on redeployment. No paid services, production seeding or administrator creation are triggered automatically.

### Further iteration

After the MVP, invite a small number of visitors and organisers to test whether the reading is useful and importing it saves effort. Use their feedback to prioritise cross-event topic filters, personal bookmarks or post-event resource emails. These are possible later features, outside the current MVP.

Document checks: both languages have matching sections, rules, wireframes and flows; Markdown fences and tables are valid; relative links resolve; product behaviour and technology choices remain consistent across the documents. These are planned acceptance criteria, not claims of completed implementation or measured business impact.
