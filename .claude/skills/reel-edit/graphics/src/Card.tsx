import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import type { Graphic } from './types';

const FONT = 'Montserrat, "DejaVu Sans", Arial, sans-serif';

// Seconds since the Sequence started -> local frame of a word timestamp.
const useLocal = (g: Graphic) => {
  const { fps } = useVideoConfig();
  return (t: number) => Math.round((t - g.start) * fps);
};

const Pop = ({ at, children }: { at: number; children: React.ReactNode }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - at, fps, config: { damping: 14, stiffness: 180 } });
  if (frame < at) return null;
  return (
    <div style={{ opacity: s, transform: `translateY(${(1 - s) * 40}px) scale(${0.92 + 0.08 * s})` }}>{children}</div>
  );
};

export const Card = ({ g, accent }: { g: Graphic; accent: string }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const local = useLocal(g);
  const end = Math.round((g.end - g.start) * fps);
  const inS = spring({ frame, fps, config: { damping: 16, stiffness: 160 } });
  const out = interpolate(frame, [end - 6, end], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const full = (g.layout ?? 'full') === 'full';
  const u = width / 1080; // scale from a 1080-wide design
  const panel: React.CSSProperties = full
    ? { position: 'absolute', inset: 0, background: 'rgba(8,8,10,0.94)' }
    : { position: 'absolute', left: 48 * u, right: 48 * u, top: height * 0.1, minHeight: height * 0.3, borderRadius: 36 * u, background: 'rgba(8,8,10,0.88)' };
  const text = (size: number, extra: React.CSSProperties = {}): React.CSSProperties => ({
    fontFamily: FONT, color: '#fff', fontSize: size * u, fontWeight: 800, lineHeight: 1.15, letterSpacing: -0.5 * u, ...extra,
  });

  let body: React.ReactNode = null;
  if (g.type === 'title') {
    body = (
      <>
        <div style={text(96, { textAlign: 'center' })}>{g.text}</div>
        {g.sub ? <div style={text(44, { color: accent, fontWeight: 700, marginTop: 28 * u, textAlign: 'center' })}>{g.sub}</div> : null}
      </>
    );
  } else if (g.type === 'list' || g.type === 'steps') {
    body = (
      <>
        {g.heading ? <div style={text(52, { color: accent, marginBottom: 36 * u })}>{g.heading}</div> : null}
        {g.items.map((it, i) => (
          <Pop key={i} at={local(it.at)}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 28 * u, marginBottom: 28 * u }}>
              <div style={{ minWidth: 84 * u, height: 84 * u, borderRadius: 42 * u, background: accent, display: 'flex', alignItems: 'center', justifyContent: 'center', ...text(44, { color: '#111' }) }}>
                {g.type === 'steps' ? i + 1 : '✓'}
              </div>
              <div style={text(56, { fontWeight: 700 })}>{it.text}</div>
            </div>
          </Pop>
        ))}
      </>
    );
  } else if (g.type === 'stat') {
    body = (
      <>
        <div style={text(180, { color: accent, textAlign: 'center', fontWeight: 900 })}>{g.value}</div>
        <div style={text(52, { textAlign: 'center', marginTop: 20 * u, fontWeight: 700 })}>{g.label}</div>
      </>
    );
  } else if (g.type === 'compare') {
    const col = (c: { title: string; lines: string[] }, hi: boolean) => (
      <div style={{ flex: 1, padding: 32 * u, borderRadius: 28 * u, background: hi ? accent : 'rgba(255,255,255,0.08)' }}>
        <div style={text(50, { color: hi ? '#111' : '#fff', marginBottom: 20 * u })}>{c.title}</div>
        {c.lines.map((l, i) => <div key={i} style={text(40, { color: hi ? '#111' : '#ddd', fontWeight: 600, marginBottom: 12 * u })}>{l}</div>)}
      </div>
    );
    body = (
      <div style={{ display: 'flex', gap: 24 * u }}>
        {col(g.left, false)}
        <Pop at={local(g.at ?? g.start)}>{null}</Pop>
        {frame >= local(g.at ?? g.start) ? col(g.right, true) : <div style={{ flex: 1 }} />}
      </div>
    );
  }

  return (
    <AbsoluteFill style={{ opacity: inS * out }}>
      <div style={{ ...panel, display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: 72 * u, transform: `scale(${0.96 + 0.04 * inS})` }}>
        {body}
      </div>
    </AbsoluteFill>
  );
};
