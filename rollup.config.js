import resolve from '@rollup/plugin-node-resolve';
import { brotliCompress } from 'zlib';
import { promisify } from 'util';
import commonjs from '@rollup/plugin-commonjs';
import { terser } from 'rollup-plugin-terser';
import styles from 'rollup-plugin-styles';
import gzipPlugin from 'rollup-plugin-gzip';

// {{{  extra fontawesome subset, need to edit
// galleryfield/static/dev/@fortawesome/fontawesome-free/css/all.css accordingly after first run.
import { fontawesomeSubset } from "fontawesome-subset";
fontawesomeSubset(
    [
        // yes, rotate-left, rotate-right, close, reset, warning, sort
        'check', 'reply', 'share', 'times', 'sync-alt', 'exclamation-triangle', 'sort',
        // add, edit, start, cancel, delete
        'plus', 'edit', 'upload', 'ban', 'trash-alt'
    ],
    'galleryfield/static/dev/@fortawesome/fontawesome-free/webfonts'
);
// }}}

// `npm run build` -> `production` is true
// `npm run dev` -> `production` is false
const production = !process.env.ROLLUP_WATCH;

const brotliPromise = promisify(brotliCompress);

const defaultPlugins = [
  resolve(),
  styles(),
  commonjs(),
  production && terser(), // minify, but only in production
  production && gzipPlugin(),
  production && gzipPlugin({
    customCompression: (content) => brotliPromise(Buffer.from(content)),
    fileName: '.br',
  })
];

export default [
  {
    input: 'galleryfield/static/js/bundle-source.js',
    output: {
      file: 'galleryfield/static/js/galleryfield-ui.js',
      format: 'iife',
      sourcemap: true,
      name: 'galleryFieldUI',
      globals: {
        jquery: "$"
      }
    },
    plugins: defaultPlugins,
    external: ["jquery", "bootstrap"]
  },
];
