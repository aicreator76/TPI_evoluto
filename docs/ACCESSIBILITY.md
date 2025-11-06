# Linee guida accessibilitÃ  (WCAG quick)

- Contrasto testo â‰¥ 4.5:1 (usa colori brand + verifica contrasto).
- Focus visibile: `:focus-visible` su link e bottoni.
- Semantica: `aria-label`, `role` per componenti custom; titoli gerarchici.
- Tastiera: tutti i controlli tab-navigabili; niente â€œkeyboard trapâ€.
- Motion: rispetta `prefers-reduced-motion`.
- Alt testuale: immagini con `alt` descrittivo; icone decorative con `aria-hidden="true"`.

## CSS minimo consigliato
```css
:focus-visible { outline: 3px solid #1e90ff; outline-offset: 2px; }
.sr-only{position:absolute;width:1px;height:1px;margin:-1px;border:0;padding:0;clip:rect(0 0 0 0);overflow:hidden;}
```
