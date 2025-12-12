-- ============================================================
-- LYNX DPI 3.0 - VIEW CATALOGO
-- File: sql/create_views_lynx_dpi_3_0_2025-12-09.sql
-- Dipendenze: tabelle catalogo DPI già importate in tpi.db
-- ============================================================

-- Pulizia eventuali vecchie view
DROP VIEW IF EXISTS vw_lynx_dpi_famiglie;
DROP VIEW IF EXISTS vw_lynx_dpi_codici;
DROP VIEW IF EXISTS vw_lynx_dpi_listino;

-- ------------------------------------------------------------
-- VIEW famiglie DPI (es. elmetti, imbracature, ecc.)
-- Adatta il nome tabella a quella reale nel DB.
-- Esempio: tpi_dpi_famiglie
-- ------------------------------------------------------------
CREATE VIEW vw_lynx_dpi_famiglie AS
SELECT
    id                  AS id_famiglia,
    famiglia            AS nome_famiglia,
    categoria_macro     AS macro_categoria,
    categoria_micro     AS sotto_categoria,
    note                AS note
FROM tpi_dpi_famiglie;  -- TODO: cambia con nome reale

-- ------------------------------------------------------------
-- VIEW codici DPI (prodotti singoli)
-- Adatta il nome tabella tpi_dpi_catalogo e le colonne.
-- ------------------------------------------------------------
CREATE VIEW vw_lynx_dpi_codici AS
SELECT
    c.id                        AS id_dpi,
    c.codice_tpi                AS codice_tpi,
    c.codice_fabbrica           AS codice_fabbrica,
    c.descrizione_breve         AS descrizione_breve,
    c.descrizione_estesa        AS descrizione_estesa,
    c.norme_en                  AS norme_en,
    c.tag_rischio               AS tag_rischio,
    c.famiglia                  AS famiglia_nome,
    c.linea_modello             AS linea_modello,
    c.tag_settore               AS settore,
    c.prezzo_listino_eur        AS prezzo_listino_eur,
    c.valuta                    AS valuta,
    c.note                      AS note,
    -- campo "sorgente" per distinguere eventuali sotto-liste (LYNX, FORESTALE, ecc.)
    'LYNX_DPI'                  AS sorgente
FROM tpi_dpi_catalogo AS c;     -- TODO: cambia con tabella reale

-- ------------------------------------------------------------
-- VIEW listino completo LYNX DPI 3.0
-- JOIN logica famiglie ↔ codici (per nome_famiglia o id_famiglia).
-- Se non hai chiavi certe, usa LEFT JOIN su nome_famiglia.
-- ------------------------------------------------------------
CREATE VIEW vw_lynx_dpi_listino AS
SELECT
    c.id_dpi                    AS id,
    c.codice_tpi                AS id_tpi,
    c.codice_fabbrica,
    c.descrizione_breve,
    c.descrizione_estesa,
    c.norme_en,
    c.tag_rischio,
    c.linea_modello,
    c.settore,
    c.prezzo_listino_eur,
    c.valuta,
    c.note,
    c.sorgente,
    f.id_famiglia,
    f.nome_famiglia             AS famiglia,
    f.macro_categoria,
    f.sotto_categoria           AS sotto_famiglia
FROM vw_lynx_dpi_codici AS c
LEFT JOIN vw_lynx_dpi_famiglie AS f
    ON c.famiglia_nome = f.nome_famiglia;
