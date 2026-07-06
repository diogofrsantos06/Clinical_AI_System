import React from 'react';

export default function Highlight({ text, term }) {
  if (text === null || text === undefined) return null;

  const str = String(text);
  const cleanTerm = (term || '').trim();

  if (!cleanTerm) return <>{str}</>;

  const escaped = cleanTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const parts = str.split(new RegExp(`(${escaped})`, 'gi'));

  if (parts.length === 1) return <>{str}</>;

  return (
    <>
      {parts.map((part, i) =>
        part.toLowerCase() === cleanTerm.toLowerCase() ? (
          <mark key={i} className="bg-amber-300 text-slate-900 rounded-sm px-0.5">
            {part}
          </mark>
        ) : (
          <React.Fragment key={i}>{part}</React.Fragment>
        )
      )}
    </>
  );
}
