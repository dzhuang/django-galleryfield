import resolve from '@rollup/plugin-node-resolve';
import { brotliCompress } from 'zlib';
import { promisify } from 'util';
import commonjs from '@rollup/plugin-commonjs';
import { terser } from 'rollup-plugin-terser';
import styles from 'rollup-plugin-styles';
import gzipPlugin from 'rollup-plugin-gzip';
import {mdiSubset} from 'materialdesignicon-subset';

// `npm run build` -> `production` is true
// `npm run dev` -> `production` is false
const production = !process.env.ROLLUP_WATCH;

const brotliPromise = promisify(brotliCompress);

const mdiFonts = [
    {name: "plus", transformOptions: {viewBox: [4, 4, 16, 16]}},
    {name: "check", transformOptions: {viewBox: [3, 3, 18, 18]}},
    {name: "trash-can", transformOptions: {viewBox: [3, 3, 18, 18]}},
    {name: "format-rotate-90", transformOptions: {viewBox: [1, 1, 22, 22]}},
    {name: "upload", transformOptions: {viewBox: [3, 3, 18, 18]}},
    {name: "cancel", transformOptions: {viewBox: [2, 2, 20, 20]}},
    {name: "reload", transformOptions: {viewBox: [2, 2, 20, 20]}},
    {name: "close", transformOptions: {viewBox: [3, 3, 18, 18]}},
    {name: "sync", transformOptions: {viewBox: [1, 1, 22, 22]}},
    "crop-rotate",
];

mdiSubset(mdiFonts, "galleryfield/static/dev/mdiFonts");

const defaultPlugins = [
  resolve(),
  styles(),
  commonjs(),
  production && terser(), // minify, but only in production
  production && gzipPlugin(),
  production && gzipPlugin({
    customCompression: (content) => brotliPromise(Buffer.from(content)),
    fileName: '.br',
  }),
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
    external: [
        "jquery",
        "bootstrap",
    ]
  },
];
