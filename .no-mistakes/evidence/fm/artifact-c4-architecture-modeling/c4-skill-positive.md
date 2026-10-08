Captain, these views model the supplied synthetic source/design description, dated 2026-10-07. Implementation and live deployment are unverified. “Review service” is the model’s chosen system name.

```mermaid
---
title: C4 System Context — Review service — source/design
---
flowchart LR
  reviewer["Reviewer<br/>Person<br/>Reviews submissions"]
  subgraph ownership["Review service — logical ownership"]
    review["Review service<br/>Software system<br/>Supports reviews and records decisions"]
  end
  identity["Identity Service<br/>External software system<br/>Provides identity functionality"]
  reviewer -->|Uses browser review interface| review
  review -->|Calls identity functionality| identity
  key["KEY: boxes = typed elements; enclosure = logical ownership.<br/>Arrows = directional actions. All elements: source/design evidence.<br/>Internal applications and stores omitted at this level."]
```

```mermaid
---
title: C4 Containers — Review service — source/design
---
flowchart LR
  reviewer["Reviewer<br/>Person<br/>Reviews submissions"]
  subgraph review["Review service — logical ownership"]
    ui["Review UI<br/>Application container: browser JavaScript<br/>Provides review interface"]
    api["Review API<br/>Application container: Node.js<br/>Records decisions and processing status<br/>Identity SDK: embedded library in this process"]
    worker["Submission worker<br/>Application container: Node.js<br/>Reads documents and updates status"]
    decisions[("Decision schema<br/>Data-store container: PostgreSQL<br/>Stores decisions; owned schema<br/>Hosted by managed database provider")]
    documents[("Submission bucket<br/>Data-store container: cloud object storage<br/>Stores submission documents; owned bucket")]
  end
  identity["Identity Service<br/>External software system<br/>Provides identity functionality"]
  reviewer -->|Operates interface; browser interaction| ui
  ui -->|Calls Review API; HTTPS JSON| api
  api -->|Calls through embedded Identity SDK; HTTPS JSON| identity
  api -->|Writes decisions; protocol unspecified| decisions
  worker -->|Reads submission documents; protocol unspecified| documents
  worker -->|Updates processing status; HTTPS JSON| api
  key["KEY: boxes = typed actors/applications/systems; cylinders = stores.<br/>Enclosure = logical ownership, not deployment or network trust.<br/>Arrows = directional actions. All elements: source/design evidence.<br/>UI = user interface; API = application programming interface;<br/>SDK = software development kit; HTTPS = secure HTTP;<br/>JSON = JavaScript Object Notation."]
```

The SDK shares the API’s process; the UI and worker are separate containers. Managed hosting does not move the owned schema or bucket outside the logical system. Hosting topology, network trust zones, and unspecified storage protocols remain unknown.

Validation receipt: `mmdc` and `mermaid` were absent from `PATH`; Node.js `v22.23.1` could not resolve `mermaid`, `@mermaid-js/mermaid-cli`, or `@mermaid-js/parser`. No parser pass or visual layout verification is claimed. No files changed, delegation performed, or services contacted.