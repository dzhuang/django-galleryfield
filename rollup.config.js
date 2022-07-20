import resolve from '@rollup/plugin-node-resolve';
import {brotliCompress} from 'zlib';
import {promisify} from 'util';
import commonjs from '@rollup/plugin-commonjs';
import {terser} from 'rollup-plugin-terser';
import styles from 'rollup-plugin-styles';
import gzipPlugin from 'rollup-plugin-gzip';
import {subsetIconfont, MdiProvider, FaFreeProvider} from 'subset-iconfont';

// `npm run build` -> `production` is true
// `npm run dev` -> `production` is false
const production = !process.env.ROLLUP_WATCH;

const brotliPromise = promisify(brotliCompress);

const mdi = new MdiProvider([
    "format-rotate-90",
    "cancel",
    "sync",
    "crop-rotate",
  ],
);

const fa = new FaFreeProvider([
    "plus",
    "check",
    "trash-can",
    "upload",
    "triangle-exclamation",
    "xmark",
  ],
);

subsetIconfont(
  [mdi, fa],
  "galleryfield/static/dev/ss-iconfont", {cssChoices: ['flipped']});

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
