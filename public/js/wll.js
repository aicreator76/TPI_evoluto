// Safe formatter per badge WLL (giorni alla scadenza)
export function formatWLLDays(dateStr, now = new Date()) {
  if (!dateStr) return { label: 'WLL: dato mancante', color: 'yellow' };
  const t = Date.parse(dateStr);
  if (!Number.isFinite(t)) return { label: 'WLL: formato non valido', color: 'red' };

  const msLeft = t - now.getTime();
  const days = Math.ceil(msLeft / 86400000);
  if (Number.isNaN(days)) return { label: 'WLL: dato non valido', color: 'red' };

  const color = days < 0 ? 'red' : (days <= 30 ? 'yellow' : 'green');
  const abs = Math.abs(days);
  const plural = abs === 1 ? 'giorno' : 'giorni';
  return { label: `WLL: ${abs} ${plural}${days < 0 ? ' (scaduto)' : ''}`, color };
}

// Esempio uso:
// const badge = formatWLLDays('2025-11-25');
// document.querySelector('#badge-wll').textContent = badge.label;
// document.querySelector('#badge-wll').dataset.color = badge.color;
