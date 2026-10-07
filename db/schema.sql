-- AfterImage Dynamic Database Schema (Zero-LLM Core)
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    event_type TEXT NOT NULL,          -- 'WindowFocus', 'FileEdit', 'TerminalCmd', 'BrowserTab'
    application TEXT,
    entity_path TEXT,
    payload_json TEXT
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE', -- 'ACTIVE', 'BLOCKED', 'PAUSED', 'COMPLETED'
    project TEXT NOT NULL,
    progress INTEGER DEFAULT 0,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS activities (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    category TEXT NOT NULL,            -- 'CODE_EDIT', 'FAILURE', 'SEARCH', 'DOCUMENT', 'TEST'
    summary TEXT NOT NULL,
    timestamp REAL NOT NULL,
    entities_json TEXT NOT NULL,
    FOREIGN KEY(task_id) REFERENCES tasks(id)
);

CREATE TABLE IF NOT EXISTS blockers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    target_failing TEXT NOT NULL,
    loop_count INTEGER NOT NULL DEFAULT 1,
    code_diff_entropy REAL DEFAULT 0.0,
    is_dead_end INTEGER DEFAULT 0,
    severity REAL DEFAULT 3.0,
    diagnosis TEXT NOT NULL,
    created_at REAL NOT NULL,
    resolved INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS causal_edges (
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,       -- 'TRIGGERS_INVESTIGATION', 'REFERENCES_DOC', 'MODIFIES_CODE', 'CAUSES_FAILURE'
    timestamp REAL NOT NULL,
    PRIMARY KEY(source_id, target_id)
);
