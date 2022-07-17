// This ensures that the '$' and jQuery aliases are set before other modules
// use them.

import jQuery from 'jquery';

window.$ = jQuery;
window.jQuery = jQuery;

import loadImage from 'blueimp-load-image';
window.loadImage = loadImage;

import Sortable from 'sortablejs';
window.Sortable = Sortable;

import Cropper from 'cropperjs';
window.Cropper = Cropper
