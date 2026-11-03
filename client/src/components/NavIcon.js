import { h } from 'vue'

// Inline stroke icons on a 24x24 grid, drawn from data so they inherit currentColor
// and avoid v-html. Unknown names fall back to a dot rather than breaking the sidebar.
const ICONS = {
  dashboard: [['rect', { x: 3, y: 3, width: 7, height: 9, rx: 1.5 }], ['rect', { x: 14, y: 3, width: 7, height: 5, rx: 1.5 }], ['rect', { x: 14, y: 12, width: 7, height: 9, rx: 1.5 }], ['rect', { x: 3, y: 16, width: 7, height: 5, rx: 1.5 }]],
  box: [['path', { d: 'M21 8l-9-5-9 5v8l9 5 9-5V8z' }], ['path', { d: 'M3 8l9 5 9-5M12 13v8' }]],
  list: [['path', { d: 'M8 6h13M8 12h13M8 18h13' }], ['circle', { cx: 4, cy: 6, r: 1 }], ['circle', { cx: 4, cy: 12, r: 1 }], ['circle', { cx: 4, cy: 18, r: 1 }]],
  wallet: [['rect', { x: 3, y: 6, width: 18, height: 14, rx: 2 }], ['path', { d: 'M3 10h18M16 15h2' }]],
  trend: [['path', { d: 'M3 17l6-6 4 4 8-8' }], ['path', { d: 'M15 7h6v6' }]],
  restock: [['path', { d: 'M20 11a8 8 0 0 0-14.9-3M4 4v4h4' }], ['path', { d: 'M4 13a8 8 0 0 0 14.9 3M20 20v-4h-4' }]],
  file: [['path', { d: 'M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5z' }], ['path', { d: 'M14 3v5h5M9 13h6M9 17h6' }]],
  menu: [['path', { d: 'M4 6h16M4 12h16M4 18h16' }]],
  close: [['path', { d: 'M6 6l12 12M18 6L6 18' }]],
  chevronLeft: [['path', { d: 'M15 6l-6 6 6 6' }]],
  chevronRight: [['path', { d: 'M9 6l6 6-6 6' }]],
  moon: [['path', { d: 'M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z' }]],
  sun: [['circle', { cx: 12, cy: 12, r: 4 }], ['path', { d: 'M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4' }]],
  dot: [['circle', { cx: 12, cy: 12, r: 3 }]]
}

export default {
  name: 'NavIcon',
  props: {
    name: { type: String, required: true },
    size: { type: Number, default: 20 }
  },
  setup(props) {
    return () =>
      h(
        'svg',
        {
          width: props.size,
          height: props.size,
          viewBox: '0 0 24 24',
          fill: 'none',
          stroke: 'currentColor',
          'stroke-width': 1.75,
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
          'aria-hidden': 'true',
          focusable: 'false'
        },
        (ICONS[props.name] || ICONS.dot).map(([tag, attrs]) => h(tag, attrs))
      )
  }
}
