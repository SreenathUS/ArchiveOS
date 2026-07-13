CREATE TABLE IF NOT EXISTS schema_migrations (
  version INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS imports (
  import_id INTEGER PRIMARY KEY AUTOINCREMENT,
  import_name TEXT NOT NULL UNIQUE,
  started_at TEXT NOT NULL,
  source_root TEXT NOT NULL,
  archive_root TEXT NOT NULL,
  source_uuid TEXT,
  manifest_path TEXT,
  status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS media (
  media_id INTEGER PRIMARY KEY AUTOINCREMENT,
  import_id INTEGER,
  source_rel TEXT NOT NULL UNIQUE,
  dest_rel TEXT,
  filename TEXT NOT NULL,
  ext TEXT NOT NULL,
  size INTEGER NOT NULL,
  sha256 TEXT,
  capture_date TEXT,
  capture_source TEXT,
  camera_model TEXT,
  lens TEXT,
  camera_serial TEXT,
  gps_lat REAL,
  gps_lon REAL,
  width INTEGER,
  height INTEGER,
  duration REAL,
  media_group TEXT,
  media_kind TEXT,
  duplicate_group TEXT,
  verified INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL,
  note TEXT,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hash_cache (
  path TEXT PRIMARY KEY,
  size INTEGER NOT NULL,
  mtime_ns INTEGER NOT NULL,
  sha256 TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_media_sha ON media(sha256);
CREATE INDEX IF NOT EXISTS idx_media_capture_date ON media(capture_date);
CREATE INDEX IF NOT EXISTS idx_media_group ON media(media_group);
