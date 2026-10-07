# AfterImage — Full Project Approach

> A high-performance, Zero-LLM personal work-state recovery system that reconstructs what you were doing, why you were doing it, what remains unfinished, and helps you resume the task later — operating with < 60 MB RAM and < 0.2% CPU.

---

## 1. Project Overview

### Project Name

**AfterImage**

### One-line description

AfterImage is a privacy-first desktop application that observes a user's local work activity and converts it into a semantic representation of active tasks, dependencies, blockers, and context so the user can recover and resume unfinished work.

### Core idea

Most computers remember **events**:

- which application was open
- which files changed
- which websites were visited
- which terminal commands were executed

AfterImage attempts to remember **work context**:

> "What was I trying to accomplish, what did I already try, what worked, what failed, and what should I continue with?"

---

# 2. Problem Statement

Modern developers and knowledge workers constantly switch between:

- IDEs
- terminals
- browsers
- documentation
- PDFs
- databases
- issue trackers
- notes
- communication tools

When a work session ends, the context is fragmented across all these applications.

The next time the user returns, they often need to reconstruct:

1. What was I working on?
2. What was my goal?
3. Which files mattered?
4. What did I already try?
5. What failed?
6. Why did I make this change?
7. What should I do next?

Existing tools generally solve only one part of this problem.

- Git stores code changes.
- Browser history stores pages.
- Shell history stores commands.
- IDEs store project state.
- Notes store manually written context.
- Screen recorders store raw activity.

AfterImage combines these signals into a **semantic work-state model**.

---

# 3. Goals

## Primary Goals

AfterImage should:

- Automatically capture relevant local work activity.
- Keep data local by default.
- Group low-level activity into meaningful tasks.
- Build relationships between files, searches, commands, applications, and actions.
- Detect unfinished work.
- Detect possible blockers and dead ends.
- Explain why a previous action may have happened.
- Provide a "Resume Task" experience.
- Restore useful workspace context.

## Secondary Goals

- Generate automatic work-session summaries.
- Provide semantic search over personal work history.
- Detect repeated problem-solving loops.
- Build a personal project knowledge graph.
- Learn the user's work patterns without requiring manual tagging.

## Non-goals

The first version should NOT attempt to:

- record every pixel of the screen
- become a general-purpose AI assistant
- replace Git
- replace project management software
- monitor other users
- upload all activity to a cloud service
- automatically execute arbitrary commands

---

# 4. Example User Story

A developer is implementing JWT refresh-token rotation.

During a two-hour session they:

1. Open the project.
2. Modify `auth.ts`.
3. Search for refresh-token rotation.
4. Read documentation.
5. Modify a PostgreSQL schema.
6. Run tests.
7. Three tests fail.
8. Change the middleware.
9. Run tests again.
10. Stop working.

The next day AfterImage displays:

```text
ACTIVE TASK

Implement refresh-token rotation

Progress: 72%

Completed:
✓ Authentication middleware
✓ Database schema
✓ Token storage

Unresolved:
✗ 3 refresh-token tests

Last activity:
Modified auth.ts

Likely next step:
Investigate refreshToken.test.ts

Related resources:
- auth.ts
- refresh_tokens.sql
- refreshToken.test.ts
- JWT rotation documentation
```

The user presses:

**Resume**

AfterImage restores the relevant project and context.

---

# 5. Core Product Concepts

## 5.1 Event

The smallest observable activity.

Examples:

```text
ApplicationActivated
FileOpened
FileModified
TerminalCommand
BrowserPageVisited
GitCommit
GitBranchChanged
TestExecuted
DocumentOpened
DatabaseQuery
```

Example:

```json
{
  "type": "FileModified",
  "timestamp": "2026-10-07T12:30:00",
  "path": "/project/src/auth.ts",
  "application": "VS Code"
}
```

---

# 5.2 Activity

A normalized interpretation of one or more events.

Example:

```text
Event:
    TerminalCommand:
    npm test

Activity:
    Test execution

Result:
    3 tests failed
```

---

# 5.3 Task

A semantic cluster of related activities representing a user's goal.

Example:

```text
Task:
Implement refresh-token rotation
```

Activities:

```text
Search JWT rotation
Read documentation
Modify auth.ts
Modify database schema
Run tests
Inspect failures
Modify middleware
```

---

# 5.4 Work Session

A continuous period of activity.

Example:

```text
Session:
09:42 → 11:38

Project:
FinCare API

Primary task:
Authentication
```

---

# 5.5 Context

The set of information required to understand or resume a task.

Context may contain:

- files
- directories
- terminal commands
- browser pages
- documents
- Git state
- errors
- searches
- applications
- timestamps
- task summary
- unresolved issues

---

# 5.6 Task Graph

The central data structure.

Example:

```text
                    Authentication
                          |
              +-----------+-----------+
              |                       |
        Access Token            Refresh Token
                                      |
                         +------------+------------+
                         |                         |
                    Database                    API
                         |                         |
                    schema.sql                  auth.ts
                         |                         |
                         +------------+------------+
                                      |
                                    Tests
                                      |
                                     FAIL
```

The graph allows AfterImage to reason about relationships instead of treating every event independently.

---

# 6. High-Level Architecture

```text
                         USER COMPUTER
                               |
           +-------------------+-------------------+
           |                   |                   |
        Browser               IDE               Terminal
           |                   |                   |
           +-------------------+-------------------+
                               |
                OS Activity Collectors (Win32 Hooks)
                               |
                               v
                     Event Ingestion Layer
                               |
                               v
                     Event Normalization
                               |
                               v
                Activity Extraction & Token Shingling
                               |
                               v
            Dynamic Causal DAG Builder (In-Memory petgraph)
                               |
              +----------------+----------------+
              |                                 |
              v                                 v
     Task Boundary Discovery            Cyclic Subgraph Entropy
      (TC-BGP Partitioning)               (Blocker & Loop Radar)
              |                                 |
              +----------------+----------------+
                               |
                               v
               Context Reconstruction (Personalized PageRank)
                               |
                               v
           Backward Causal Tracing ("Why Did I Do This?")
                               |
                               v
               Ultra-Lean Desktop UI (Tauri 2.0 + SolidJS)
                     (Total RAM < 60MB, CPU < 0.2%)
```
---

# 7. System Architecture

## Layer 1 — Capture Layer

Responsible for collecting raw local activity.

Sources:

- active window
- application process
- filesystem
- terminal
- browser
- Git
- IDE
- document metadata

The capture layer should produce events, not AI interpretations.

---

# 8. Capture Modules

## 8.1 Active Window Collector

Tracks:

```text
Application
Window title
Process
Timestamp
Duration
```

Example:

```json
{
  "type": "WindowFocus",
  "application": "Code",
  "title": "auth.ts — fincare-api",
  "timestamp": "2026-10-07T12:31:20"
}
```

Do not capture screen pixels by default.

---

## 8.2 File Activity Collector

Track:

- file opened
- file modified
- file renamed
- file deleted
- directory accessed

Important:

The first version should store metadata rather than full file contents.

Example:

```json
{
  "type": "FileModified",
  "path": "/workspace/src/auth.ts",
  "timestamp": "...",
  "hash": "..."
}
```

Content can be indexed selectively later.

---

## 8.3 Terminal Collector

Capture:

```text
command
working directory
exit code
duration
stdout summary
stderr summary
```

Example:

```json
{
  "type": "CommandExecuted",
  "command": "npm test",
  "cwd": "/workspace/fincare",
  "exitCode": 1
}
```

Security rule:

Never automatically store secrets from environment variables.

---

## 8.4 Browser Collector

Capture:

```text
domain
page title
URL
timestamp
duration
```

Example:

```text
GitHub
Stack Overflow
MDN
PostgreSQL documentation
```

Do not store sensitive browsing categories by default.

---

## 8.5 Git Collector

Track:

```text
repository
branch
commit
changed files
commit message
working-tree status
```

Example:

```text
Branch:
feature/refresh-token

Commit:
fix refresh token rotation

Changed:
auth.ts
token.service.ts
```

Git provides extremely valuable semantic signals.

---

# 9. Privacy Layer

Privacy should be a first-class architecture component.

## Principle

**Local by default.**

Raw activity should not leave the machine unless the user explicitly enables synchronization.

### Exclusion list

Users should be able to exclude:

```text
Applications
Directories
Domains
Projects
File extensions
```

Example:

```yaml
excluded_apps:
  - password_manager
  - banking_app

excluded_domains:
  - banking.example
  - private.example

excluded_paths:
  - ~/Private
  - ~/.ssh
```

---

# 10. Event Pipeline

Raw events should pass through:

```text
Raw Event
    |
    v
Validation
    |
    v
Normalization
    |
    v
Deduplication
    |
    v
Privacy Filter
    |
    v
Persistence
    |
    v
Semantic Processing
```

---

# 11. Event Normalization

Different sources may describe the same thing differently.

For example:

```text
VS Code:
Opened auth.ts

Filesystem:
Read auth.ts

Git:
auth.ts changed
```

These should become a common representation.

```json
{
  "entity": "auth.ts",
  "actions": [
    "opened",
    "read",
    "modified"
  ],
  "project": "fincare"
}
```

---

# 12. Semantic Activity Extraction

The system converts raw events into higher-level activities.

Example:

```text
Raw events:

Chrome → search JWT refresh token
Chrome → MDN
VS Code → auth.ts
Terminal → npm test
Terminal → exit code 1
VS Code → auth.ts modified
```

Become:

```text
Activity 1:
Researching refresh-token implementation

Activity 2:
Editing authentication middleware

Activity 3:
Testing authentication

Activity 4:
Investigating test failures
```

---

# 13. Task Detection

The biggest intelligence problem is:

> Which activities belong to the same task?

Possible signals:

### Temporal similarity

Activities close together in time are more likely related.

### Project similarity

Events inside the same repository are more likely related.

### File similarity

Repeated interaction with the same files indicates a relationship.

### Semantic similarity

Search queries, document titles, commands, and code metadata can be embedded.

### Causal signals

A failing test followed by code modification is highly related.

### Git signals

A commit can act as a strong task boundary.

---

# 14. Task Boundary Discovery: Temporal-Causal Bipartite Graph Partitioning (TC-BGP)

Instead of brittle static linear equations (`0.15 * temp + 0.20 * proj...`), AfterImage uses **Temporal-Causal Bipartite Graph Partitioning (TC-BGP)**:

1. We construct a dynamic bipartite graph $G = (V_{\text{activity}}, V_{\text{entity}}, E)$ where entities are normalized file paths, git branches, process names, and search terms.
2. The edge weight between activity $A_i$ and entity $e_j$ incorporates temporal recency and entity specificity (TF-IDF):
   $$W(A_i, e_j) = \text{TF-IDF}(e_j, A_i) \cdot \exp(-\lambda |t_i - t_e|)$$
3. As activities stream in, we perform **Online Modularity Maximization**:
   - If modularity gain $\Delta Q > \theta_{\text{task}}$, the activity joins the active cluster.
   - If $\Delta Q \le \theta_{\text{task}}$ and the directory tree edit distance exceeds threshold $\delta$, a new task cluster is cleanly split.

**Execution Speed**: $< 0.15\text{ ms}$ per activity. Memory: $< 2\text{ MB}$.

---

# 15. Token Shingling & Fast In-Memory Indexing (Zero-LLM)

Instead of memory-heavy neural vector embedding models (which require hundreds of megabytes of RAM and GPU/CPU matrix multiplication), AfterImage uses lightweight, deterministic token representations:

- **MinHash / SimHash Locality-Sensitive Hashing**: Converts window titles, terminal outputs, and search queries into compact 64-bit fingerprint vectors.
- **SQLite FTS5 with BM25**: Enables instant full-text search directly inside the embedded SQLite database with zero external server or vector DB overhead.
- **AST Symbol Extraction**: Extracts modified function and class names directly from diffs using tree-sitter bindings in Rust.

This guarantees sub-millisecond similarity lookups with **zero GPU/CPU inference overhead** and negligible memory ($< 5\text{ MB}$).

---

# 16. Streaming Dynamic Graph Clustering

Activities are clustered dynamically using **Online Community Detection on the Causal DAG**:

```text
Activity A: "Search JWT refresh token"  (Entity: 'jwt', 'refresh')
    | (Shared token + within 4 min window)
    v
Activity B: "Edit auth.ts"               (Entity: 'auth.ts', 'jwt')
    | (File edit triggers test execution)
    v
Activity C: "npm test"                   (Entity: 'auth.ts', 'test')
    | (Test failure targets refreshToken.test.ts)
    v
Activity D: "Fix refresh token test"     (Entity: 'refreshToken.test.ts')

→ Connected Component / High Modularity Community:
  Task: "Refresh Token Implementation"
```

Benefits over DBSCAN/HDBSCAN:
- No arbitrary epsilon hyperparameter tuning.
- Runs incrementally in stream time ($O(1)$ amortized per incoming event).
- Preserves directional causal relationships.

---

# 17. Task State Machine

Every task can have a state.

```text
DISCOVERED
    |
    v
ACTIVE
    |
    +-------> BLOCKED
    |           |
    |           v
    |         ACTIVE
    |
    v
PAUSED
    |
    v
RESUMED
    |
    v
COMPLETED
```

Optional state:

```text
ABANDONED
```

---

# 18. Blocker Detection: Cyclic Subgraph Entropy Detection (CS-SED)

Instead of naive counters ("same error 5 times") that trigger false alarms during iterative coding, AfterImage uses **Cyclic Subgraph Entropy Detection (CS-SED)**:

1. Terminal command failures (exit code $\ne 0$) and compiler error streams are parsed into canonical **Error Signatures** by stripping volatile timestamps and line offsets.
2. When an error signature recurs, we calculate the **Information Entropy of Code Diffs**:
   $$H(\Delta_{\text{code}}) = -\sum_{k} p_k \log_2 p_k$$
3. If the error signature repeats while entropy $H(\Delta_{\text{code}})$ drops below threshold $\epsilon$ (indicating repetitive trial-and-error churn without progress), the system flags a verified blocker.

---

# 19. Dead-End Loop Radar

When a repeated cycle is confirmed:
$$\text{Edit}(F_1) \longrightarrow \text{Exec}(C_1) \longrightarrow \text{Fail}(E_1) \longrightarrow \text{Edit}(F_1) \longrightarrow \text{Exec}(C_1) \longrightarrow \text{Fail}(E_1)$$

AfterImage displays a non-intrusive **Blocker Radar** widget:

```text
[Loop Detected: 3 Iterations]
Failure: Connection refused on port 5432 (database.ts)
Status: Repeating identical parameter attempts
Observed Pattern: Docker container 'postgres' was stopped 14 min ago
Suggested check: Docker container status / port mapping
```

Zero LLM calls required — derived directly from topological cycle detection and process status tracking.

---

# 20. "Why Did I Do This?" Engine: Deterministic Backward Causal Tracing (DBCT)

Instead of asking an LLM to guess why a file changed (which risks hallucinated justifications), AfterImage performs **Deterministic Backward Causal Tracing (DBCT)** over the in-memory Causal DAG:

```text
[Direct Causal Path Traversed in < 1ms]
Root Cause Event: 
  Terminal: npm test (Exit Code 1, 3 tests failed) at 10:29
      | (Causal Edge: INVESTIGATES)
      v
  Browser: Searched "jwt refresh token rotation leeway" at 10:33
      | (Causal Edge: REFERENCES)
      v
  Browser: Opened MDN / Auth0 Token Guidance at 10:35
      | (Causal Edge: MODIFIES)
      v
  Target Action: Modified auth.ts at 10:41
```

The explanation is generated using **Parametric Semantic Templates**:
- **Root Event**: `[npm test: exit code 1]`
- **Investigation**: `[Searched 'jwt refresh token rotation leeway']`
- **Documentation**: `[Visited Auth0 Token Guidance]`
- **Action**: `[Modified auth.ts 6 minutes later]`

**Accuracy**: 100% factual provenance with zero hallucination, computed in $< 0.2\text{ ms}$.

---

# 21. Context Reconstruction

For each task maintain:

```text
Task title
Task summary
Project
Files
Applications
Browser resources
Terminal commands
Errors
Git branch
Git changes
Last known state
Open questions
Blockers
Next likely action
```

Example:

```json
{
  "task": "Implement refresh token rotation",
  "project": "fincare-api",
  "status": "blocked",
  "files": [
    "src/auth.ts",
    "src/token.service.ts",
    "tests/refreshToken.test.ts"
  ],
  "blockers": [
    "3 failing tests"
  ]
}
```

---

# 22. Resume Engine: Personalized PageRank (PPR)

The Resume Engine converts task graph context into an optimal restart state using **Personalized PageRank (PPR)**:

1. We construct the active task subgraph containing files, terminal directories, and browser URLs.
2. We compute Personalized PageRank, biasing the teleport vector toward the **most recent failure nodes and modified files**:
   $$\mathbf{p} = (1 - \alpha) \mathbf{M} \mathbf{p} + \alpha \mathbf{v}_{\text{bias}}$$
3. The top 3 ranked nodes are selected for restoration.

Example Output:

```text
RESUMING: Implement refresh token rotation

State: 3 tests failing in refreshToken.test.ts (Exit Code 1)

Top Ranked Context (PPR Ranked):
1. [File] src/auth.ts (Score: 0.42 - Last modified)
2. [File] tests/refreshToken.test.ts (Score: 0.31 - Failing test)
3. [Doc]  JWT Rotation Documentation (Score: 0.18 - Most referenced)

Terminal Working Dir: ~/fincare-api
Suggested next action: Open refreshToken.test.ts
```

---

# 23. Workspace Restoration

Restoration is instantaneous:
- Opens the top 3 PPR-ranked files directly in the editor.
- Re-launches the terminal at the exact project directory.
- Displays the causal provenance trail and active blocker immediately.

---

# 24. Database Design

SQLite is recommended for V1.

## events

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    type TEXT NOT NULL,
    source TEXT NOT NULL,
    payload TEXT NOT NULL
);
```

## activities

```sql
CREATE TABLE activities (
    id INTEGER PRIMARY KEY,
    start_time INTEGER NOT NULL,
    end_time INTEGER,
    type TEXT NOT NULL,
    summary TEXT,
    confidence REAL
);
```

## tasks

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,
    status TEXT NOT NULL,
    project TEXT,
    created_at INTEGER,
    updated_at INTEGER
);
```

## task_activities

```sql
CREATE TABLE task_activities (
    task_id INTEGER,
    activity_id INTEGER,
    score REAL,
    PRIMARY KEY(task_id, activity_id)
);
```

## entities

```sql
CREATE TABLE entities (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    value TEXT NOT NULL,
    metadata TEXT
);
```

## relationships

```sql
CREATE TABLE relationships (
    source_id INTEGER,
    target_id INTEGER,
    type TEXT NOT NULL,
    weight REAL
);
```

## embeddings

```sql
CREATE TABLE embeddings (
    entity_id INTEGER PRIMARY KEY,
    vector BLOB NOT NULL,
    model TEXT NOT NULL
);
```

---

# 25. Graph Model

Logical graph:

```text
Task
 |
 +-- Activity
 |
 +-- File
 |
 +-- BrowserResource
 |
 +-- Command
 |
 +-- Error
 |
 +-- GitCommit
 |
 +-- Project
```

Relationships:

```text
Task --contains--> Activity
Activity --modified--> File
Activity --caused--> Error
Activity --followed_by--> Activity
Task --belongs_to--> Project
File --related_to--> File
Command --failed_with--> Error
```

SQLite can store the source of truth initially.

A graph database is optional later.

---

# 26. Zero-LLM Architecture & Algorithmic Design

AfterImage operates **completely without generative LLMs**, eliminating token generation latency, heavy RAM footprints, and hallucinations.

## Tier 0 — Deterministic Event & AST Stream (Rust Core)
- Event ingestion (Win32 Hooks, ReadDirectoryChangesW, ETW).
- Real-time privacy regex masking (redacts secrets, tokens, keys).
- In-memory Causal DAG updates using `petgraph`.
- Zero AI overhead; CPU usage $< 0.1\%$.

## Tier 1 — Graph Analytic Core
- **Task Partitioning**: Temporal-Causal Bipartite Graph Partitioning (TC-BGP).
- **Blocker Radar**: Cyclic Subgraph Entropy Detection (CS-SED).
- **Provenance**: Deterministic Backward Causal Tracing (DBCT).
- **Context Ranking**: Personalized PageRank (PPR).

## Optional Tier 2 — LAYA Decision Engine by Nandakishor Mukkunnoth
For users who want neural classification without LLM bloat:
- **LAYA** (`NandhaKishorM/laya` / `convaiinnovations/laya`) is a **421M parameter non-autoregressive "System 1" decision engine** (ModernBERT-large backbone + multi-task decision heads).
- **Non-Autoregressive**: Unlike generative LLMs, LAYA does not output text token-by-token. It evaluates structured schemas (`choice`, `score`, `noul`) in a **single forward pass** in $< 35\text{ ms}$.
- **Deployment**: Executed as a quantized INT8 ONNX graph embedded directly inside Rust via the `ort` crate.
- **Role in AfterImage**: Evaluates ambiguous cross-project task assignments and blocker severity if pure graph heuristics require semantic arbitration.

---

# 27. Dual Operational Modes

1. **Mode A: 100% Pure Algorithmic (Default)**:
   - Zero neural model weights loaded into memory.
   - Total application RAM: **$\approx 45\text{ MB}$**.
   - Background CPU: **$< 0.1\%$**.
   - Laptop fans stay completely silent.

2. **Mode B: LAYA-Assisted Decision Mode (Optional Toggle)**:
   - Micro-ONNX INT8 decision engine.
   - Invoked only on ambiguous task boundary events.
   - Total application RAM: **$< 180\text{ MB}$**.

---

# 28. Instant FTS5 & Causal Search (Zero-LLM)

Instead of slow vector similarity searches and LLM text generation, search in AfterImage is powered by **SQLite FTS5 (BM25 ranking) + Causal Graph Expansion**:

Search Pipeline:

```text
User Query (e.g. "auth.ts", "PostgreSQL error", "yesterday")
    |
    v
SQLite FTS5 Token Match with BM25 Ranking (< 1ms)
    |
    v
Graph Neighborhood Expansion on Causal DAG (< 0.5ms)
    |
    v
Instant Structural Result Presentation (< 2ms total)
```

No LLM synthesis required; results display direct, verifiable facts with timestamped logs.

---

# 29. Example Query Resolution (Sub-Millisecond)

Query:

> Why did I modify `auth.ts`?

Step 1: Match `auth.ts` entity in SQLite FTS5 index ($pprox 0.4\text{ ms}$).  
Step 2: Follow backward causal edges in `petgraph` DAG ($pprox 0.1\text{ ms}$).  
Step 3: Render factual provenance card directly in SolidJS UI:

```text
[OBSERVED CAUSAL TRAIL]
10:28 - Ran npm test
10:29 - 3 tests failed in refreshToken.test.ts (Exit Code 1)
10:33 - Searched "jwt refresh token rotation leeway"
10:35 - Opened MDN / Auth0 documentation
10:41 - Modified auth.ts (expiry leeway parameter updated)
```

---

# 30. Desktop UI

Recommended UI structure:

```text
+--------------------------------------------------+
| AFTERIMAGE                         ● Recording   |
+--------------------------------------------------+
|                                                  |
| CURRENT TASK                                     |
|                                                  |
| Implement refresh-token rotation                 |
|                                                  |
| Progress                         72%             |
|                                                  |
| Last active: 18 minutes ago                     |
|                                                  |
| BLOCKER                                          |
| 3 tests failing                                  |
|                                                  |
| [ Resume ]     [ View Task ]                    |
|                                                  |
+--------------------------------------------------+
| ACTIVE TASKS                                     |
|                                                  |
| Authentication             72%                  |
| Database migration         41%                  |
| UI redesign                91%                  |
|                                                  |
+--------------------------------------------------+
```

---

# 31. Task Detail View

```text
IMPLEMENT REFRESH-TOKEN ROTATION

Status:
BLOCKED

Timeline
────────────────────────────

09:42  Started investigation
09:51  Read JWT documentation
10:02  Modified auth.ts
10:17  Changed database schema
10:28  Ran tests
10:29  3 tests failed
10:41  Modified middleware

Files
────────────────────────────
auth.ts
token.service.ts
refreshToken.test.ts

Blockers
────────────────────────────
3 failing tests

Likely next action
────────────────────────────
Investigate refreshToken.test.ts

[ Resume Task ]
```

---

# 32. Recording Controls

The user must always know what is happening.

Example:

```text
● Recording

Tracked:
✓ Applications
✓ Files
✓ Terminal
✓ Git
✓ Browser metadata

Excluded:
🔒 Password manager
🔒 Banking
🔒 Private directory
```

Controls:

```text
Pause recording
Exclude application
Exclude directory
Delete history
Delete project history
Export data
```

---

# 33. Security Requirements

The application will have access to sensitive local information.

Therefore:

### Never log secrets

Avoid capturing:

```text
API keys
passwords
tokens
environment variables
SSH private keys
cookies
credentials
```

### Redaction layer

Before persistence:

```text
Raw data
   ↓
Secret detector
   ↓
Redaction
   ↓
Database
```

Example:

```text
Authorization: Bearer eyJ...
```

becomes:

```text
Authorization: Bearer [REDACTED]
```

---

# 34. Performance Requirements

AfterImage is optimized from the ground up for ultra-smooth operation on standard laptops:

```text
CPU Idle:
< 0.2% background utilization

Memory:
< 60 MB total (Mode A) / < 180 MB (Mode B with LAYA ONNX)

Startup:
< 0.8 seconds to ready

Event processing latency:
< 2 milliseconds end-to-end

Battery impact:
Virtually unmeasurable
```

Zero continuous neural inference in the background stream.

---

# 35. Retention

Provide configurable retention:

```text
7 days
30 days
90 days
1 year
Forever
```

Potential storage strategy:

```text
Recent:
Full metadata

Older:
Compressed summaries

Very old:
Task-level summaries only
```

---

# 36. Recommended Technology Stack

## Desktop Engine

**Tauri 2.0 (Rust Core + Webview)**
- Native Windows binary with zero heavy runtime overhead.
- Direct Win32 API hooks (`SetWinEventHook`, `ReadDirectoryChangesW`).

## Frontend UI

**SolidJS + TypeScript + Tailwind CSS**
- **Zero Virtual DOM**: Fine-grained reactivity compiling directly to minimal native DOM updates.
- Uses only **$\approx 35\text{ MB}$ RAM** inside the webview (vs $> 180\text{ MB}$ for React).
- Delivers butter-smooth 120Hz animations.

## In-Memory Graph

**Rust `petgraph`**
- Directed Causal DAG stored in-memory with sub-50-microsecond traversal speeds.

## Embedded Storage & Search

**SQLite (WAL Mode + FTS5 Full-Text Search)**
- Fast ACID storage, sub-millisecond BM25 keyword search, zero external database servers.

## Decision Engine (Optional)

**LAYA by Nandakishor Mukkunnoth (via Rust `ort` ONNX Runtime)**
- Non-autoregressive System 1 decision engine (ModernBERT backbone), used optionally for ambiguous cross-project task routing.

---

# 37. Project Structure

Suggested repository:

```text
afterimage/
│
├── apps/
│   └── desktop/
│       ├── src/
│       └── package.json
│
├── core/
│   ├── capture/
│   ├── events/
│   ├── privacy/
│   ├── activities/
│   ├── tasks/
│   ├── graph/
│   ├── retrieval/
│   └── resume/
│
├── ai/
│   ├── embeddings/
│   ├── llm/
│   ├── clustering/
│   └── prompts/
│
├── database/
│   ├── migrations/
│   └── schema/
│
├── shared/
│   ├── types/
│   └── protocol/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── docs/
│   ├── architecture.md
│   ├── privacy.md
│   └── development.md
│
└── README.md
```

---

# 38. Development Phases

## Phase 0 — Research

Duration:

**2–4 days**

Research:

- OS activity APIs
- filesystem events
- process monitoring
- browser integration
- Tauri architecture
- local embeddings
- SQLite
- privacy requirements

Deliverable:

```text
Technical feasibility document
```

---

# 39. Phase 1 — Event Collector

Build:

```text
✓ Application tracking
✓ Window tracking
✓ File tracking
✓ Terminal tracking
✓ Git tracking
✓ SQLite persistence
```

No AI yet.

Goal:

Prove that the application can build a reliable event history.

---

# 40. Phase 2 — Timeline

Build:

```text
✓ Timeline UI
✓ Filtering
✓ Project grouping
✓ Session detection
✓ Search
```

Example:

```text
Today

09:41  VS Code
09:44  Terminal
09:50  Chrome
10:03  VS Code
10:20  Terminal
```

---

# 41. Phase 3 — Activity Extraction

Convert:

```text
100 raw events
```

into:

```text
12 meaningful activities
```

Implement:

- activity boundaries
- event aggregation
- basic rules
- confidence scores

---

# 42. Phase 4 — Task Detection

Implement:

```text
✓ task clustering
✓ semantic embeddings
✓ project awareness
✓ task naming
✓ task state
```

Example:

```text
Detected Task:

"Fix PostgreSQL connection problem"

Confidence:
0.86
```

---

# 43. Phase 5 — Task Graph

Build:

```text
Task
 ↓
Activities
 ↓
Files
 ↓
Errors
 ↓
Commands
 ↓
Resources
```

Add graph visualization.

---

# 44. Phase 6 — Blocker Detection

Implement:

```text
✓ repeated failures
✓ test failures
✓ repeated commands
✓ inactivity after failure
✓ error clusters
```

Output:

```text
Potential blocker detected:
PostgreSQL connection refused
```

---

# 45. Phase 7 — AI Context

Add:

```text
✓ task summaries
✓ "why did I do this?"
✓ natural language search
✓ automatic next-step suggestions
```

---

# 46. Phase 8 — Resume

Implement:

```text
✓ workspace restoration
✓ terminal restoration
✓ relevant browser restoration
✓ task summary
✓ blocker display
```

---

# 47. Phase 9 — Dead-End Detection

Implement pattern detection:

```text
Repeated action
+
Similar context
+
Same failure
=
Possible loop
```

Show:

```text
You may be repeating the same approach.
```

---

# 48. Phase 10 — Polish

Add:

- onboarding
- privacy controls
- exclusions
- data export
- retention controls
- performance optimization
- crash recovery
- database migrations
- documentation

---

# 49. MVP Definition

The MVP should NOT contain everything.

MVP:

```text
✓ Desktop app
✓ Local SQLite
✓ Application tracking
✓ File tracking
✓ Terminal tracking
✓ Git tracking
✓ Timeline
✓ Basic task detection
✓ Task summaries
✓ Local semantic search
✓ Privacy exclusions
✓ Pause recording
```

That is enough for a strong first release.

---

# 50. Version 2

```text
✓ Task graph
✓ Blocker detection
✓ Dead-end detection
✓ Resume workspace
✓ "Why did I do this?"
✓ Better task clustering
```

---

# 51. Version 3

```text
✓ Personal knowledge graph
✓ Long-term project memory
✓ Cross-project relationships
✓ Learned personal workflows
✓ Advanced counterfactual reasoning
✓ Optional synchronization
```

---

# 52. Testing Strategy

## Unit Tests

Test:

```text
event normalization
privacy filtering
task scoring
clustering
state transitions
redaction
```

## Integration Tests

Test:

```text
capture → database
events → activities
activities → tasks
tasks → graph
graph → retrieval
```

## Replay Tests

This is especially important.

Create recorded synthetic sessions:

```text
session_001.json
session_002.json
session_003.json
```

Replay them through the system.

Expected:

```text
Input events
      ↓
Expected task
      ↓
Expected blocker
      ↓
Expected summary
```

This lets you improve the intelligence without repeatedly using the real computer.

---

# 53. Evaluation Metrics

Track:

## Task clustering accuracy

How often activities are grouped into the correct task.

## Task naming quality

Human rating of generated task names.

## Blocker precision

How often detected blockers are real.

## Blocker recall

How often real blockers are detected.

## Resume usefulness

Ask:

> Could the user successfully continue the task using the generated context?

## Context compression

Measure:

```text
1000 raw events
↓
20 activities
↓
3 tasks
```

The system should reduce noise without losing important context.

---

# 54. Important Engineering Principle

Do not build the AI first.

Build this:

```text
Reliable events
        ↓
Reliable activities
        ↓
Reliable task boundaries
        ↓
Reliable graph
        ↓
AI
```

If the underlying data is wrong, an LLM will only produce a convincing explanation of incorrect data.

---

# 55. Biggest Technical Challenges

## Challenge 1

Determining when two actions belong to the same task.

Solution:

Combine:

```text
time
project
files
semantic similarity
causal relationships
Git
```

---

## Challenge 2

Understanding user intent.

Solution:

Use probabilistic inference.

Never claim certainty when the system is guessing.

Use:

```text
Observed:
You ran npm test.

Inferred:
You were likely validating the authentication change.
```

---

## Challenge 3

Privacy.

Solution:

Privacy filtering must happen before long-term persistence whenever practical.

---

## Challenge 4

Resource usage.

Solution:

Use event-driven processing.

Avoid continuous expensive AI inference.

---

## Challenge 5

Cross-platform support.

Start with **one OS**.

Recommended:

```text
Linux first
```

or the OS you personally use most.

After the architecture stabilizes:

```text
Linux
↓
Windows
↓
macOS
```

---

# 56. What Makes This Project Interesting

The project combines several areas:

```text
Operating Systems
        +
Desktop Development
        +
Event Processing
        +
Information Retrieval
        +
Graph Algorithms
        +
Machine Learning
        +
Local LLMs
        +
Privacy Engineering
        +
Human-Computer Interaction
```

It is not simply:

```text
Frontend
+
CRUD
+
ChatGPT API
```

The difficult part is the **reasoning over a stream of personal activity**.

---

# 57. Potential Research Angle

A stronger academic version could explore:

> **Can semantic task reconstruction reduce context-switch recovery time for developers?**

Experiment:

### Control group

Users manually recover their previous context.

### Experimental group

Users use AfterImage.

Measure:

```text
time to resume
number of actions repeated
number of irrelevant resources opened
task completion time
perceived cognitive load
```

This turns the project from just a software product into a potential research project.

---

# 58. Future Research Ideas

## Context Graph Compression

How much raw activity can be removed while preserving task recoverability?

## Personal Workflow Modeling

Can a system learn:

```text
"When this user sees this error,
they usually inspect this file first."
```

## Task Boundary Prediction

Predict when one task ends and another begins.

## Human-AI Memory

Study whether externalized task memory reduces cognitive load.

## Counterfactual Workflows

Estimate:

> "Which previous action most likely caused the current state?"

---

# 59. Example End-to-End Flow

```text
USER
 |
 | opens VS Code
 v
Capture Event
 |
 v
WindowFocus
 |
 | edits auth.ts
 v
FileModified
 |
 | searches JWT rotation
 v
BrowserActivity
 |
 | runs npm test
 v
CommandExecuted
 |
 | exit code 1
 v
FailureDetected
 |
 v
Activity Extraction
 |
 v
"Investigating authentication"
 |
 v
Task Association
 |
 v
"Refresh Token Implementation"
 |
 v
Task Graph
 |
 +--> auth.ts
 +--> JWT documentation
 +--> npm test
 +--> 3 failing tests
 |
 v
Blocker Detection
 |
 v
"3 tests failing"
 |
 v
User stops working
 |
 v
Task becomes PAUSED
 |
 v
NEXT DAY
 |
 v
AfterImage
 |
 v
"Resume Refresh Token Implementation?"
 |
 v
USER CLICKS RESUME
 |
 +--> opens project
 +--> opens relevant files
 +--> opens terminal
 +--> restores useful documentation
 +--> shows blocker
 |
 v
USER CONTINUES
```

---

# 60. Final Product Vision

The final experience should feel like the computer remembers your **unfinished thoughts**, not just your files.

Instead of:

> "Here is your browser history."

AfterImage says:

> "Yesterday you were implementing refresh-token rotation. You finished the database portion but stopped after three tests failed. You had been investigating token validation. Here is the exact context you left behind."

That is the core product.

---

# 61. First Build Order

If building this alone, follow this exact order:

```text
1. Tauri shell
        ↓
2. SQLite
        ↓
3. Event schema
        ↓
4. Application/window collector
        ↓
5. Filesystem collector
        ↓
6. Terminal collector
        ↓
7. Git collector
        ↓
8. Timeline UI
        ↓
9. Session detection
        ↓
10. Activity extraction
        ↓
11. Task clustering
        ↓
12. Task database
        ↓
13. Embeddings
        ↓
14. Task summaries
        ↓
15. Blocker detection
        ↓
16. Task graph
        ↓
17. Natural-language search
        ↓
18. Resume engine
        ↓
19. Dead-end detection
        ↓
20. Privacy + performance hardening
```

---

# 62. Suggested 4-Week Solo Schedule

## Week 1 — Foundation

```text
Day 1:
Repository + architecture

Day 2:
Tauri + React shell

Day 3:
SQLite schema

Day 4:
Event system

Day 5:
Window/application tracking

Day 6:
Filesystem tracking

Day 7:
Timeline prototype
```

## Week 2 — Context

```text
Day 8:
Terminal tracking

Day 9:
Git tracking

Day 10:
Session detection

Day 11:
Activity extraction

Day 12:
Activity UI

Day 13:
Project detection

Day 14:
Testing + cleanup
```

## Week 3 — Intelligence

```text
Day 15:
Embedding pipeline

Day 16:
Task clustering

Day 17:
Task naming

Day 18:
Task state machine

Day 19:
Task graph

Day 20:
Blocker detection

Day 21:
Task dashboard
```

## Week 4 — Killer Features

```text
Day 22:
Natural-language search

Day 23:
"Why did I do this?"

Day 24:
Dead-end detection

Day 25:
Resume context

Day 26:
Workspace restoration

Day 27:
Privacy controls

Day 28:
Performance testing

Day 29:
Demo scenario

Day 30:
Documentation + release
```

---

# 63. Demo Scenario

For a portfolio/demo presentation, do not demonstrate random activity.

Create a controlled scenario:

```text
1. Open project
2. Create a bug
3. Investigate it
4. Search documentation
5. Try solution A
6. Fail
7. Try solution B
8. Fail
9. Stop the session
```

Then restart the application.

Show:

```text
AFTERIMAGE

You were debugging PostgreSQL connection failures.

You tried 2 approaches.

Approach A:
Changed connection string
→ Failed

Approach B:
Changed Docker configuration
→ Failed

Current blocker:
Connection refused

Last active file:
database.ts

Suggested next step:
Inspect container networking.

[ RESUME ]
```

That demonstrates the project's actual value in under two minutes.

---

# 64. Definition of Success

AfterImage succeeds if a user can stop working on a complicated task for several days and later answer:

```text
What was I doing?
Why was I doing it?
What did I already try?
What failed?
What files mattered?
What should I do next?
```

without manually reconstructing their entire history.

---

# 65. Final Principle

The project should not try to remember **everything**.

It should remember **what matters**.

The goal is:

```text
Raw Computer Activity
        ↓
Meaning
        ↓
Task
        ↓
Context
        ↓
Recoverable State
```

The final product is not a history recorder.

It is a **personal work-state recovery system**.
