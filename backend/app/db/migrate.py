"""Database migration and schema sync helper for SQLite/PostgreSQL."""
from sqlalchemy import inspect, text, Engine
from app.core.logging import logger


def run_migrations(engine: Engine):
    """
    Checks existing tables for missing columns added in schema updates and cleanly alters tables.
    """
    try:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        if "facts" in table_names:
            columns = {col["name"] for col in inspector.get_columns("facts")}
            
            # Phase 2 columns to add if missing
            new_columns = [
                ("fiscal_year", "VARCHAR(32)"),
                ("quarter", "VARCHAR(16)"),
                ("geography", "VARCHAR(64)"),
                ("scope", "VARCHAR(64)"),
                ("definition", "TEXT"),
                ("source_section", "VARCHAR(128)"),
                ("value_status", "VARCHAR(32) DEFAULT 'ACTUAL'"),
                ("embedding_id", "VARCHAR(128)"),
                ("indexing_status", "VARCHAR(32) DEFAULT 'PENDING'"),
            ]

            with engine.connect() as conn:
                for col_name, col_type in new_columns:
                    if col_name not in columns:
                        logger.info(f"Applying schema update: adding column '{col_name}' to 'facts' table.")
                        conn.execute(text(f"ALTER TABLE facts ADD COLUMN {col_name} {col_type}"))
                conn.commit()

        if "fact_relationships" in table_names:
            rel_columns = {col["name"] for col in inspector.get_columns("fact_relationships")}
            new_rel_columns = [
                ("value_comparison", "JSON"),
                ("context_comparison", "JSON"),
                ("supporting_evidence", "JSON"),
                ("uncertainty_notes", "TEXT"),
                ("reasoning_method", "VARCHAR(32) DEFAULT 'DETERMINISTIC'"),
            ]
            with engine.connect() as conn:
                for col_name, col_type in new_rel_columns:
                    if col_name not in rel_columns:
                        logger.info(f"Applying schema update: adding column '{col_name}' to 'fact_relationships' table.")
                        conn.execute(text(f"ALTER TABLE fact_relationships ADD COLUMN {col_name} {col_type}"))
                conn.commit()
    except Exception as e:
        logger.warning(f"Schema migration warning: {e}")
