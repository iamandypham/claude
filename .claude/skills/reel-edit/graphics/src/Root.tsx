import { Composition } from 'remotion';
import { Reel } from './Reel';
import type { ReelProps } from './types';

const defaults: ReelProps = { video: '', width: 1080, height: 1920, fps: 30, duration: 5, graphics: [] };

export const RemotionRoot = () => (
  <Composition
    id="Reel"
    component={Reel}
    defaultProps={defaults}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={150}
    calculateMetadata={({ props }) => ({
      width: props.width,
      height: props.height,
      fps: props.fps,
      durationInFrames: Math.ceil(props.duration * props.fps),
    })}
  />
);
