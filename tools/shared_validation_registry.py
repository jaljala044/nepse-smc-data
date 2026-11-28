"""Content-addressed cache for deterministic NEPSE dataset validation.

This cache reuses technical validation for byte-identical inputs across repositories.
It does NOT establish source authorization, source lineage, completeness, cross-source
agreement, or canonical-data approval. Those remain separate acceptance gates.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ValidationKey:
    content_sha256: str
    dataset_kind: str
    schema_version: str
    validator_version: str

    def cache_id(self) -> str:
        payload = json.dumps(
            {
                "content_sha256": self.content_sha256,
                "dataset_kind": self.dataset_kind,
                "schema_version": self.schema_version,
                "validator_version": self.validator_version,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Return a streaming SHA-256 digest; files are never loaded wholly in memory."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ValidationRegistry:
    """SQLite-backed cache shared by collectors/importers using the same registry DB."""

    def __init__(self, database: str | Path):
        self.database = Path(database)
        self.database.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS validation_cache (
                    cache_id TEXT PRIMARY KEY,
                    content_sha256 TEXT NOT NULL,
                    dataset_kind TEXT NOT NULL,
                    schema_version TEXT NOT NULL,
                    validator_version TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('passed', 'failed')),
                    report_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database, timeout=30)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def make_key(
        path: str | Path,
        dataset_kind: str,
        schema_version: str,
        validator_version: str,
    ) -> ValidationKey:
        if not all((dataset_kind, schema_version, validator_version)):
            raise ValueError("dataset_kind, schema_version and validator_version are required")
        return ValidationKey(
            sha256_file(path), dataset_kind, schema_version, validator_version
        )

    def lookup(self, key: ValidationKey) -> dict[str, Any] | None:
        """Return a prior technical result, or None when this exact contract is unseen."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT status, report_json, created_at FROM validation_cache WHERE cache_id = ?",
                (key.cache_id(),),
            ).fetchone()
        if row is None:
            return None
        return {
            "status": row["status"],
            "report": json.loads(row["report_json"]),
            "created_at": row["created_at"],
            "cache_hit": True,
            "content_sha256": key.content_sha256,
        }

    def record(
        self,
        key: ValidationKey,
        status: str,
        report: dict[str, Any] | None = None,
    ) -> None:
        """Persist a deterministic technical result; never label it source-approved."""
        if status not in {"passed", "failed"}:
            raise ValueError("status must be 'passed' or 'failed'")
        report_json = json.dumps(report or {}, sort_keys=True, separators=(",", ":"))
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO validation_cache (
                    cache_id, content_sha256, dataset_kind, schema_version,
                    validator_version, status, report_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cache_id) DO UPDATE SET
                    status=excluded.status, report_json=excluded.report_json,
                    created_at=CURRENT_TIMESTAMP
                """,
                (
                    key.cache_id(),
                    key.content_sha256,
                    key.dataset_kind,
                    key.schema_version,
                    key.validator_version,
                    status,
                    report_json,
                ),
            )
