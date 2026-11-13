/**
 * The 24 × 24 UI icons shared by the studio's components (`components/Icon.tsx`), the chooser and the lite page.
 * Everything is drawn in currentColor.
 */

/** 24 × 24 icons: stroked at 1.8 px, except the names in FILLED_ICONS. */
export const ICONS: Record<string, string> = {
  play: 'M7 4.5v15l12-7.5z',
  stop: 'M6 6h12v12H6z',
  dice: 'M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2zm3 4a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm8 7a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm-4-3.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z',
  star: 'M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.9L12 16.9l-5.3 2.8 1-5.9-4.2-4.1 5.9-.8z',
  trash: 'M5 7h14M10 7V4.5h4V7m-7 0 1 13h8l1-13',
  plus: 'M12 5v14M5 12h14',
  upload: 'M12 16V4m0 0L7 9m5-5 5 5M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3',
  mic: 'M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3zM5 11a7 7 0 0 0 14 0M12 18v3',
  undo: 'M9 7 4 12l5 5M4 12h11a5 5 0 0 1 0 10h-2',
  redo: 'M15 7l5 5-5 5M20 12H9a5 5 0 0 0 0 10h2',
  refresh: 'M20 11a8 8 0 1 0-2.3 5.7M20 5v6h-6',
  x: 'M6 6l12 12M18 6 6 18',
  save: 'M5 4h11l3 3v13H5zM8 4v5h7V4M8 20v-6h8v6',
  download: 'M12 4v12m0 0-5-5m5 5 5-5M4 20h16',
  up: 'M6 15l6-6 6 6',
  down: 'M6 9l6 6 6-6',
  edit: 'M4 20h4L19 9l-4-4L4 16zM14 6l4 4',
  /** Edit speech: scissors over a waveform (Direct → Edit, Edit sources). */
  'edit-speech': 'M6 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM6 14a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM20 5 8.5 13M20 19 8.5 11M12 12h2',
  home: 'M4 11 12 4l8 7v9h-5v-6H9v6H4z',
  copy: 'M9 9h10v11H9zM5 15V4h10',
  wand: 'M5 19 15 9m2-5v3m0 0v3m0-3h3m-3 0h-3M6 5v2m0 0v2m0-2h2m-2 0H4',
  expand: 'M9 4H4v5M15 4h5v5M9 20H4v-5M15 20h5v-5',
  sliders: 'M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0M14 4v4M8 10v4M16 16v4',
  globe: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM3 12h18M12 3c2.5 2.5 3.8 5.5 3.8 9s-1.3 6.5-3.8 9c-2.5-2.5-3.8-5.5-3.8-9S9.5 5.5 12 3z',
  film: 'M4 5h16v14H4zM8 5v14M16 5v14M4 9h4M4 15h4M16 9h4M16 15h4',
  sun: 'M12 8a4 4 0 1 0 0 8a4 4 0 1 0 0-8zM12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4',
  moon: 'M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z',
  alert: 'M12 3.5 2.5 20h19zM12 10v4.5M12 17.2v.1',
  left: 'M15 6l-6 6 6 6',
  right: 'M9 6l6 6-6 6',
  more: 'M5 10.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm7 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm7 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z',
  speaker: 'M4 9h4l5-4v14l-5-4H4zM16 9a4 4 0 0 1 0 6M18.5 6.5a7.5 7.5 0 0 1 0 11',
  brush: 'M15 4l5 5-8 8-5-5zM7 12l5 5-2 2a3 3 0 0 1-4.2 0l-1.6-1.6a3 3 0 0 1 0-4.2z',
  gear: 'M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7zM12 2.5v2.3M12 19.2v2.3M2.5 12h2.3M19.2 12h2.3M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6',
};

export const FILLED_ICONS: Record<string, true> = { play: true, stop: true, dice: true, more: true };
