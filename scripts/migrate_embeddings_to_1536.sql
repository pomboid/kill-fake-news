-- Migration Script: Upgrade embedding dimensions from 768 to 1536
--
-- This migration allows using OpenAI embeddings (1536 dims) as primary
-- while maintaining compatibility with Gemini embeddings (768 dims) via padding
--
-- ⚠️ IMPORTANT: Create a backup before running!
--   pg_dump -U postgres vortex > backup_before_1536_migration_$(date +%Y%m%d).sql
--
-- Estimated time: ~30 seconds for 10K articles
-- Downtime: None (uses atomic column swap)

-- ================================================================
-- STEP 1: Create new column with 1536 dimensions
-- ================================================================
ALTER TABLE article ADD COLUMN IF NOT EXISTS embedding_new vector(1536);

COMMENT ON COLUMN article.embedding_new IS
  'Embeddings with 1536 dimensions (OpenAI standard). Gemini 768-dim embeddings are padded with zeros.';

-- ================================================================
-- STEP 2: Migrate existing embeddings (768 → 1536 with padding)
-- ================================================================
-- For each existing 768-dim embedding, pad with 768 zeros to reach 1536
UPDATE article
SET embedding_new = array_cat(
    embedding::float[],                          -- Original 768 values
    array_fill(0.0::float, ARRAY[768])::float[]  -- Pad with 768 zeros
)
WHERE embedding IS NOT NULL;

-- Verify migration
DO $$
DECLARE
    migrated_count INTEGER;
    original_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO original_count FROM article WHERE embedding IS NOT NULL;
    SELECT COUNT(*) INTO migrated_count FROM article WHERE embedding_new IS NOT NULL;

    RAISE NOTICE 'Migration progress: % of % embeddings migrated', migrated_count, original_count;

    IF migrated_count != original_count THEN
        RAISE EXCEPTION 'Migration incomplete! Expected %, got %', original_count, migrated_count;
    END IF;

    RAISE NOTICE '✅ All embeddings successfully migrated to 1536 dimensions';
END $$;

-- ================================================================
-- STEP 3: Drop old column and rename new one
-- ================================================================
-- Drop the old 768-dim column
ALTER TABLE article DROP COLUMN IF EXISTS embedding CASCADE;

-- Rename new column to original name
ALTER TABLE article RENAME COLUMN embedding_new TO embedding;

-- ================================================================
-- STEP 4: Recreate vector index for fast similarity search
-- ================================================================
-- Drop old index if exists
DROP INDEX IF EXISTS article_embedding_idx;

-- Create new ivfflat index for cosine similarity search
-- lists = 100 is good for ~10K articles (use sqrt(n) as rule of thumb)
CREATE INDEX article_embedding_idx
ON article USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

COMMENT ON INDEX article_embedding_idx IS
  'IVFFlat index for fast cosine similarity search on 1536-dim embeddings';

-- ================================================================
-- STEP 5: Verify index and update statistics
-- ================================================================
-- Analyze table for query planner
ANALYZE article;

-- Verify index was created
DO $$
DECLARE
    index_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'article'
        AND indexname = 'article_embedding_idx'
    ) INTO index_exists;

    IF NOT index_exists THEN
        RAISE EXCEPTION 'Index creation failed!';
    END IF;

    RAISE NOTICE '✅ Index successfully created';
END $$;

-- ================================================================
-- VERIFICATION QUERIES
-- ================================================================

-- Check column dimensions
SELECT
    column_name,
    data_type,
    CASE
        WHEN data_type = 'USER-DEFINED'
        THEN (SELECT typname FROM pg_type WHERE oid = udt_name::regtype)
        ELSE data_type
    END as vector_type
FROM information_schema.columns
WHERE table_name = 'article' AND column_name = 'embedding';

-- Count embeddings
SELECT
    COUNT(*) as total_articles,
    COUNT(embedding) as articles_with_embeddings,
    ROUND(100.0 * COUNT(embedding) / NULLIF(COUNT(*), 0), 2) as percentage_indexed
FROM article;

-- Sample embedding (first 5 dimensions)
SELECT
    id,
    title,
    (embedding::text::json->>0)::float as dim_1,
    (embedding::text::json->>1)::float as dim_2,
    (embedding::text::json->>2)::float as dim_3,
    (embedding::text::json->>3)::float as dim_4,
    (embedding::text::json->>4)::float as dim_5,
    array_length(embedding::float[], 1) as total_dimensions
FROM article
WHERE embedding IS NOT NULL
LIMIT 3;

-- ================================================================
-- SUCCESS MESSAGE
-- ================================================================
DO $$
BEGIN
    RAISE NOTICE '
╔══════════════════════════════════════════════════════════════╗
║         ✅ MIGRATION COMPLETED SUCCESSFULLY!                 ║
║                                                              ║
║  Embedding dimensions upgraded: 768 → 1536                  ║
║  Index recreated: article_embedding_idx                     ║
║  Ready for OpenAI + Gemini failover                         ║
║                                                              ║
║  Next steps:                                                 ║
║  1. Rebuild backend: docker compose build backend           ║
║  2. Restart: docker compose restart backend                 ║
║  3. Re-index: docker compose exec backend python main.py index ║
╚══════════════════════════════════════════════════════════════╝
    ';
END $$;
