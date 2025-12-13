/* DEMO FULL — dati locali (fallback se API non risponde / CORS) */
window.WOW_DEMO = {
  dpi: [
    {codice:"DPI-ELM-001", descrizione:"Elmetto dielettrico EN 397 con jugulare", famiglia:"TESTA", giorni:120, revisione_ok:true, ultima_rev:"2025-10-02"},
    {codice:"DPI-IMB-002", descrizione:"Imbracatura anticaduta 2 punti con anello dorsale", famiglia:"ANTICADUTA", giorni:25, revisione_ok:true, ultima_rev:"2025-11-20"},
    {codice:"DPI-FUN-003", descrizione:"Cordino doppio con assorbitore EN 355", famiglia:"ANTICADUTA", giorni:-3, revisione_ok:false, ultima_rev:"2024-12-01"},
    {codice:"DPI-CAR-004", descrizione:"Carrucola doppia EN 12278", famiglia:"ACCESSORI FUNI", giorni:90, revisione_ok:true, ultima_rev:"2025-09-14"},
    {codice:"DPI-MOS-005", descrizione:"Moschettone tripla ghiera EN 362", famiglia:"CONNETTORI", giorni:70, revisione_ok:true, ultima_rev:"2025-08-19"},
    {codice:"DPI-DIS-006", descrizione:"Discensore autobloccante EN 12841", famiglia:"DISPOSITIVI", giorni:40, revisione_ok:true, ultima_rev:"2025-10-31"},
    {codice:"DPI-ASC-007", descrizione:"Ascensore per fune EN 567", famiglia:"DISPOSITIVI", giorni:15, revisione_ok:true, ultima_rev:"2025-11-28"},
    {codice:"DPI-GUA-008", descrizione:"Guanti protezione meccanica EN 388", famiglia:"MANI", giorni:200, revisione_ok:true, ultima_rev:"2025-06-01"},
    {codice:"DPI-OCCH-009", descrizione:"Occhiali protettivi EN 166", famiglia:"VISTA", giorni:160, revisione_ok:true, ultima_rev:"2025-07-10"},
    {codice:"DPI-AUR-010", descrizione:"Cuffie antirumore EN 352", famiglia:"UDITO", giorni:55, revisione_ok:true, ultima_rev:"2025-09-22"},
    {codice:"DPI-MAS-011", descrizione:"Mascherina FFP3 EN 149", famiglia:"VIE RESP.", giorni:30, revisione_ok:true, ultima_rev:"2025-11-12"},
    {codice:"DPI-SCA-012", descrizione:"Scarpe S3 SRC EN ISO 20345", famiglia:"PIEDI", giorni:240, revisione_ok:true, ultima_rev:"2025-05-05"},
    {codice:"DPI-ALP-013", descrizione:"Casco alpinismo EN 12492", famiglia:"TESTA", giorni:10, revisione_ok:true, ultima_rev:"2025-12-02"},
    {codice:"DPI-ANC-014", descrizione:"Ancoraggio provvisorio EN 795-B", famiglia:"ANCORAGGI", giorni:-15, revisione_ok:false, ultima_rev:"2024-11-11"},
    {codice:"DPI-RET-015", descrizione:"Dispositivo retrattile EN 360 (10m)", famiglia:"ANTICADUTA", giorni:5, revisione_ok:true, ultima_rev:"2025-12-05"},
    {codice:"DPI-TRE-016", descrizione:"Treppiede recupero EN 795", famiglia:"RECUPERO", giorni:110, revisione_ok:true, ultima_rev:"2025-09-01"},
    {codice:"DPI-VERR-017", descrizione:"Verricello recupero (kit)", famiglia:"RECUPERO", giorni:18, revisione_ok:true, ultima_rev:"2025-11-25"},
    {codice:"DPI-COR-018", descrizione:"Cordino posizionamento EN 358", famiglia:"ANTICADUTA", giorni:62, revisione_ok:true, ultima_rev:"2025-10-12"},
    {codice:"DPI-LIN-019", descrizione:"Linea vita temporanea in fettuccia EN 795-B", famiglia:"LINEE VITA", giorni:78, revisione_ok:true, ultima_rev:"2025-09-30"},
    {codice:"DPI-KIT-020", descrizione:"Kit anticaduta completo (imbr.+cord.+mosch.)", famiglia:"ANTICADUTA", giorni:33, revisione_ok:true, ultima_rev:"2025-11-10"}
  ],

  accessori: [
    {codice:"ACC-GAN-001", descrizione:"Gancio di ancoraggio in acciaio INOX", famiglia:"SOTTOGANCIO", disponibilita:"Disponibile"},
    {codice:"ACC-LVG-002", descrizione:"Linea vita temporanea in fettuccia", famiglia:"LINEE VITA", disponibilita:"Stock limitato"},
    {codice:"ACC-CON-003", descrizione:"Connettore girevole per funi in fibra", famiglia:"ACCESSORI FUNI", disponibilita:"Non disponibile"},
    {codice:"ACC-PLA-004", descrizione:"Piastra di ancoraggio INOX", famiglia:"ANCORAGGI", disponibilita:"Disponibile"},
    {codice:"ACC-CAR-005", descrizione:"Carrucola singola alta efficienza", famiglia:"ACCESSORI FUNI", disponibilita:"Disponibile"},
    {codice:"ACC-BOR-006", descrizione:"Borsa DPI anticaduta rinforzata", famiglia:"TRASPORTO", disponibilita:"Stock limitato"},
    {codice:"ACC-SEG-007", descrizione:"Segnaletica area lavori in quota", famiglia:"CANTIERE", disponibilita:"Disponibile"},
    {codice:"ACC-LAN-008", descrizione:"Lanyard attrezzi (tool lanyard)", famiglia:"CANTIERE", disponibilita:"Disponibile"}
  ],

  sottogancio: [
    {codice:"SG-IKAR-001", descrizione:"Paranco manuale 500 kg", famiglia:"SOTTOGANCIO", stato:"OK"},
    {codice:"SG-IKAR-002", descrizione:"Bilancino certificato 2T", famiglia:"SOTTOGANCIO", stato:"In revisione"},
    {codice:"SG-IKAR-003", descrizione:"Grillo alta resistenza WLL 3.25T", famiglia:"SOTTOGANCIO", stato:"Scaduto"},
    {codice:"SG-IKAR-004", descrizione:"Fascia sollevamento 2T 3m", famiglia:"SOTTOGANCIO", stato:"OK"},
    {codice:"SG-IKAR-005", descrizione:"Golfare M16 certificato", famiglia:"SOTTOGANCIO", stato:"OK"},
    {codice:"SG-IKAR-006", descrizione:"Catena grado 80 (kit)", famiglia:"SOTTOGANCIO", stato:"In revisione"}
  ],

  movimenti: [
    {ts:"2025-12-12 09:12", tipo:"ASSEGNAZIONE", ref:"DPI-IMB-002", note:"Assegnato a Operatore: Rossi (HSE)"},
    {ts:"2025-12-12 09:16", tipo:"CHECK PRE-USO", ref:"DPI-IMB-002", note:"Foto ok • AI OK • Autorizzato"},
    {ts:"2025-12-12 10:01", tipo:"USO", ref:"DPI-IMB-002", note:"Lavoro quota — cantiere A"},
    {ts:"2025-12-12 12:40", tipo:"RITORNO", ref:"DPI-IMB-002", note:"Rientro magazzino"},
    {ts:"2025-12-12 14:05", tipo:"REVISIONE", ref:"DPI-FUN-003", note:"Segnalato assorbitore da sostituire"},
    {ts:"2025-12-12 16:22", tipo:"ORDINE", ref:"ACC-PLA-004", note:"INOX — ordine aperto grosso cliente"},
    {ts:"2025-12-13 08:10", tipo:"SCADENZA", ref:"DPI-ANC-014", note:"Scaduto — blocco utilizzo"},
    {ts:"2025-12-13 09:33", tipo:"REVISIONE", ref:"SG-IKAR-002", note:"Bilancino 2T — test + certificato"},
    {ts:"2025-12-13 11:02", tipo:"OK", ref:"DPI-RET-015", note:"Retrattile — revisione OK"},
    {ts:"2025-12-13 11:18", tipo:"ASSEGNAZIONE", ref:"DPI-RET-015", note:"Assegnato a Operatore: Bianchi"}
  ]
};
