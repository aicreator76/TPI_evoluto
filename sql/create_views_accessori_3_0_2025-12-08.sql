-- =========================================================
-- VIEW ACCESSORI 3.0 – TPI_evoluto
-- Data: 2025-12-08
--
-- NOTE:
-- - Non cancelliamo nulla, usiamo IF NOT EXISTS dove possibile.
-- - Le strutture sono pensate per:
--     * panoramica famiglie
--     * unione codici (morsetti / catena G8 / Tycan)
--     * listino completo per API / BI / n8n
-- =========================================================

-- ---------------------------------------------------------
-- 1) VIEW famiglie (pass-through)
-- ---------------------------------------------------------
DROP VIEW IF EXISTS vw_accessori_famiglie_listino;

CREATE VIEW vw_accessori_famiglie_listino AS
SELECT
    *
FROM tpi_accessori_famiglie;


-- ---------------------------------------------------------
-- 2) VIEW codici (unione morsetti / catena G8 / Tycan)
--    Assumiamo schema omogeneo generato dall'importer TPI.
--    Aggiungiamo una colonna "sorgente" per identificare il tipo.
-- ---------------------------------------------------------
DROP VIEW IF EXISTS vw_accessori_codici_listino;

CREATE VIEW vw_accessori_codici_listino AS
SELECT
    m.*,
    'MORSETTI' AS sorgente
FROM tpi_accessori_morsetti AS m

UNION ALL

SELECT
    g.*,
    'CATENA_G8' AS sorgente
FROM tpi_accessori_catena_g8 AS g

UNION ALL

SELECT
    t.*,
    'TYCAN' AS sorgente
FROM tpi_accessori_tycan AS t;


-- ---------------------------------------------------------
-- 3) VIEW listino completo
--    Per ora è un alias diretto della VIEW codici.
--    In futuro si potrà JOIN-are con le famiglie se servirà.
-- ---------------------------------------------------------
DROP VIEW IF EXISTS vw_accessori_listino_completo;

CREATE VIEW vw_accessori_listino_completo AS
SELECT
    *
FROM vw_accessori_codici_listino;
