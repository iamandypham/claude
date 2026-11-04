export type Item = { text: string; at: number };
export type Base = { start: number; end: number; layout?: 'full' | 'top' };
export type Graphic =
  | (Base & { type: 'title'; text: string; sub?: string })
  | (Base & { type: 'list' | 'steps'; heading?: string; items: Item[] })
  | (Base & { type: 'stat'; value: string; label: string; proof: string })
  | (Base & { type: 'compare'; left: { title: string; lines: string[] }; right: { title: string; lines: string[] }; at?: number });

export type ReelProps = {
  video: string;
  width: number;
  height: number;
  fps: number;
  duration: number;
  accent?: string;
  graphics: Graphic[];
};
