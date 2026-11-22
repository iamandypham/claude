import { AbsoluteFill, OffthreadVideo, Sequence, staticFile, useVideoConfig } from 'remotion';
import { Card } from './Card';
import type { ReelProps } from './types';

export const Reel = (props: ReelProps) => {
  const { fps } = useVideoConfig();
  const accent = props.accent ?? '#FECB00';
  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {props.video ? <OffthreadVideo src={staticFile(props.video)} /> : null}
      {props.graphics.map((g, i) => {
        const from = Math.round(g.start * fps);
        const dur = Math.max(1, Math.round((g.end - g.start) * fps));
        return (
          <Sequence key={i} from={from} durationInFrames={dur} layout="none">
            <Card g={g} accent={accent} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
