(function (factory) {
  'use strict';
  factory(window.jQuery, window.loadImage, window.Sortable, window.Cropper);
})(function ($, loadImage, Sortable, Cropper) {
    'use strict';

    $.blueimp.fileupload.prototype._specialOptions.push(
        'hiddenFileInput',
        'editModalId',
        'editModalImgId',
        'sortableOptions',
        'cropperResultMessageBoxSelector',
        'cropperButtonDivSelector',
        'cropperButtonSelector',
        'statusDataName',
        'filesDataToInputDataFunction',
        'csrfCookieFunction',
    );

    $.widget(
        'blueimp.fileupload', $.blueimp.fileupload, {

            options: {
                hiddenFileInput: undefined,
                editModalId: undefined,
                editModalImgId: undefined,
                cropperResultMessageBoxSelector: undefined,
                cropperButtonDivSelector: undefined,
                cropperStatusBtnSelector: undefined,
                cropperRotateBtnSelector: undefined,
                sortableOptions:undefined,
                statusDataName: undefined,
                csrfCookieFunction: undefined,

                getNumberOfUploadedFiles: function () {
                    return this.filesContainer.children('.template-download')
                        .not('.processing').length;
                },

                added: function (e, data) {
                    if (e.isDefaultPrevented()) {
                        return false;
                    }

                    const $this = $(this),
                        that = $this.data('blueimp-fileupload') ||
                            $this.data('fileupload');

                    if (!data.files) return false;
                    if (data.replaceChild && data.replaceChild.length){
                        if (that._trigger('replace', e, data) !== false)
                        {delete data.replaceChild;}
                    }

                    // todo: check if edit is allowed, for example, gif is not allowed in chrome.
                    $(data.context).find('.edit').prop('disabled', false);
                    that._toggleFileuploadButtonBarButtonDisplay();
                },

                replace: function (e, data) {
                    if (e.isDefaultPrevented()) {
                        return false;
                    }
                    const $this = $(this),
                        that = $this.data('blueimp-fileupload') ||
                            $this.data('fileupload');
                    $(data.context).replaceAll(data.replaceChild);
                    that._trigger('replaced', e, data);
                },

                submit: function (e, data) {
                    const $this = $(this),
                        that = $this.data('blueimp-fileupload') ||
                            $this.data('fileupload'),
                        options = that.options;

                    data.formData = {
                        "thumbnail_size":  options.previewMaxWidth.toString() + "x" + options.previewMaxHeight.toString(),
                    };
                    if (options.csrfCookieFunction !== undefined) {
                        data.formData.csrfmiddlewaretoken = options.csrfCookieFunction()
                    }
                },

                failed: function(e, data) {
                    if (e.isDefaultPrevented()) {
                        return false;
                    }
                    $(data.context).find('.edit').prop('disabled', false).addClass("hidden").end();

                    const that = $(this).data('blueimp-fileupload') || $(this).data('fileupload');
                    that._toggleFileuploadButtonBarButtonDisplay()._toggleFileuploadButtonBarDelete();
                },

                completed: function (e, data) {
                    if (e.isDefaultPrevented()) {
                        return false;
                    }
                    const that = $(this).data('blueimp-fileupload') || $(this).data('fileupload');
                    that._toggleFileuploadButtonBarButtonDisplay()._toggleFileuploadButtonBarDelete();
                    that._trigger("post_completed", e, data);
                    that._fillInHiddenInputs();
                },

                destroyed: function (e, data) {
                    if (e.isDefaultPrevented()) {
                        return false;
                    }
                    const that = $(this).data('blueimp-fileupload') ||
                            $(this).data('fileupload');
                    that._trigger('completed', e, data);
                    that._trigger('finished', e, data);
                    that._trigger('post-destroy', e, data);

                    that._toggleFileuploadButtonBarButtonDisplay()._toggleFileuploadButtonBarDelete();
                },

                sortableUpdate: function (e, data) {
                    const that = $(this).data('blueimp-fileupload') ||
                            $(this).data('fileupload');
                    data.context = $(this);
                    that._trigger('completed', e, data);
                    that._trigger('finished', e, data);
                },
            },

            _fillIn: function (input, files) {
                const input_data = files.length ? JSON.stringify(files) : "";
                input.val(this.options.filesDataToInputDataFunction(input_data));
                if (input.hasClass("initializing")){
                    // prevent initialization from trigger inputChanged events.
                    input.removeClass("initializing")
                } else {
                    this._trigger("inputChanged");
                }
            },
            _fillInHiddenInputs: function () {
                const filesInput = this.options.hiddenFileInput,
                  files_data = [];

                // get input files_data
                this.options.filesContainer.children('.template-download')
                        .not('.processing').find('.preview').each(function () {
                            files_data.push($(this).data("pk"));
                        });

                this._fillIn(filesInput, files_data);
                },

            _initEventHandlers: function () {
                this._super();
                const filesContainer = this.options.filesContainer;
                this._on(filesContainer, {
                    'click .edit': this._editHandler
                });
                this._on(this.element, {
                    'change .toggle': this._toggleFileuploadButtonBarDeleteDisable
                });
            },

            _toggleFileuploadButtonBarDeleteDisable: function() {
                this.element.find('.fileupload-buttonbar')
                    .find('.delete')
                    .prop(
                        'disabled',
                        !(this.element.find('.toggle').is(':checked'))
                    );
            },

            _toggleFileuploadButtonBarButtonDisplay: function() {
                const filesContainer = this.options.filesContainer,
                    bool = filesContainer.find('.template-upload').length === 0;
                this.element.find('.fileupload-buttonbar')
                    .find('.start, .cancel')
                    .css("display", bool ? "none" : "")
                    .prop("disabled", bool)
                    .end();
                return this;
            },

            _toggleFileuploadButtonBarDelete: function () {
                const that = this.element,
                    disabledBool = that.find(".toggle:checked").length === 0,
                    displayBool = !(this.options.getNumberOfUploadedFiles());
                that.find('.fileupload-buttonbar')
                    .find('.delete')
                    .css("display", displayBool ? "none" : "").prop("disabled", disabledBool).end()
                    .find(".toggle")
                    .css("display", displayBool ? "none" : "")
                    .end();
                return this;
            },

            _editHandler: function (e) {
                e.preventDefault();

                const $button = $(e.currentTarget),
                    options = this.options,
                    $fileupload = this.element,
                    template = $button.closest('.template-upload,.template-download'),
                    editType = template.hasClass("template-download") ? "download" : "upload",
                    $editModal = options.editModalId,
                    $editImg = options.editModalImgId;

                if (editType === "upload") {
                    const data = template.data("data");
                    if (!data) {
                        $button.prop("disabled", true);
                        return;
                    }
                    const mod = data.files[0];
                    let orig;
                    $.each(data.originalFiles, function (i, v) {
                        if (v.name === mod.name) {
                            orig = v;
                            return true;
                        }
                    });
                    if (!orig) {
                        return;
                    }

                    $editImg.prop('src', loadImage.createObjectURL(orig));
                    $editImg.processCroppedCanvas = function (result) {
                        $editModal.modal('hide');
                        options.cropperButtonSelector.prop("disabled", true);
                        template.find(".btn").prop("disabled", true);

                        // cheat maxNumberOfFiles count minus 1
                        data.context.addClass('processing');
                        result.toBlob(function (blob) {
                            blob.name = mod.name;
                            $fileupload.fileupload(
                                'add', {
                                    files: [blob],
                                    replaceChild: $(data.context)
                                }
                            );
                        }, orig.type);
                    };
                }

                if (editType === "download") {
                    $editImg.attr('src', $button.closest(".template-download").find(".preview").find("a").attr("href"));
                    $editImg.submitData = function (result) {
                        const messageBox = options.cropperResultMessageBoxSelector,
                            formData = {
                                "cropped_result": JSON.stringify(result),
                                "thumbnail_size":  options.previewMaxWidth.toString() + "x" + options.previewMaxHeight.toString(),
                            };

                        if (options.csrfCookieFunction !== undefined) {
                            formData.csrfmiddlewaretoken = options.csrfCookieFunction()
                        }

                        options.cropperButtonSelector.prop("disabled", true);
                        $editImg.cropper.disable();
                        $.ajax({
                            method: "POST",
                            url: $button.data("action"),
                            data: formData,
                        })
                            .always(function () {
                            })
                            .done(function (data) {
                                options.done.call($fileupload,
                                    $.Event('done'),
                                    {
                                        result: data,
                                        context: $button.closest(".template-download")
                                    });
                                if (data.message){
                                    messageBox.html("<span class='alert alert-success'>" + data.message +"</span>")}
                                $editModal.data("new", false);
                                    setTimeout(function () {
                                        if(!$editModal.data("new")){$editModal.modal('hide')}
                                    }, 1000);
                            })
                            .fail(function (response) {
                                if (response.message)
                                {messageBox.html("<span class='alert alert-danger'>" + response.message + "</span>");}
                            });
                        return false;
                    };
                }

                $editImg.rotateCanvas = function () {
                    const contData = $editImg.cropper.getContainerData(),
                      canvData = $editImg.cropper.getCanvasData(),
                      newWidth = canvData.width * (contData.height / canvData.height);
                    let newCanvData;

                    if (newWidth >= contData.width) {
                        const newHeight = canvData.height * (contData.width / canvData.width);
                        newCanvData = {
                            height: newHeight,
                            width: contData.width,
                            top: (contData.height - newHeight) / 2,
                            left: 0
                        };
                    } else {
                        newCanvData = {
                            height: contData.height,
                            width: newWidth,
                            top: 0,
                            left: (contData.width - newWidth) / 2
                        };
                    }
                    $editImg.cropper.setCanvasData(newCanvData).setCropBoxData(newCanvData);
                    options.cropperButtonSelector.prop("disabled", false);
                };

                $editModal.modal('show', [$editImg, editType]);
            },

            _initEditModalId: function () {
                const options = this.options;
                if (options.editModalId === undefined) {
                    options.editModalId = this.element.find(".edit-modal");
                } else if (!(options.editModalId instanceof $)) {
                    options.editModalId = $(options.editModalId);
                }
            },

            _initEditModalImgId: function () {
                const options = this.options;
                if (options.editModalImgId === undefined) {
                    options.editModalImgId = this.element.find(".modal-image");
                } else if (!(options.editModalImgId instanceof $)) {
                    options.editModalImgId = $(options.editModalImgId);
                }
            },

            _initCropperResultMessageBoxSelector: function () {
                const options = this.options;
                if (options.cropperResultMessageBoxSelector === undefined) {
                    options.cropperResultMessageBoxSelector = this.element.find(".cropper-message");
                } else if (!(options.cropperResultMessageBoxSelector instanceof $)) {
                    options.cropperResultMessageBoxSelector = $(options.cropperResultMessageBoxSelector);
                }
            },

            _initCropperButtonDivSelector: function () {
                const options = this.options;
                if (options.cropperButtonDivSelector === undefined) {
                    options.cropperButtonDivSelector = this.element.find(".cropper-btns");
                } else if (!(options.cropperButtonDivSelector instanceof $)) {
                    options.cropperButtonDivSelector = $(options.cropperButtonDivSelector);
                }
            },

            _initCropperButtonSelector: function () {
                const options = this.options;
                options.cropperButtonSelector = options.cropperButtonDivSelector.find(".btn")
            },

            _initCropperStatusBtnSelector: function () {
                const options = this.options;
                if (options.cropperStatusBtnSelector === undefined) {
                    options.cropperStatusBtnSelector = this.element.find('.cropper-status-btns .btn');
                } else if (!(options.cropperStatusBtnSelector instanceof $)) {
                    options.cropperStatusBtnSelector = $(options.cropperStatusBtnSelector);
                }
            },

            _initCropperRotateBtnSelector: function () {
                const options = this.options;
                if (options.cropperRotateBtnSelector === undefined) {
                    options.cropperRotateBtnSelector = this.element.find(".cropper-rotate-btns .btn");
                } else if (!(options.cropperRotateBtnSelector instanceof $)) {
                    options.cropperRotateBtnSelector = $(options.cropperRotateBtnSelector);
                }
            },

            _initEditModalEventHandler: function(){
                const $editModal = this.options.editModalId,
                    that = this,
                    options = that.options;
                let $image, editType, croppStartingData, cropperElement;
                $editModal.on('show.bs.modal', function (e) {
                    $image = e.relatedTarget[0];
                    cropperElement = $image[0];
                    editType = e.relatedTarget[1];
                })
                    .on('shown.bs.modal', function (e) {
                        $(this).data('new', true);
                        that._trigger("modalshownevent", e, true);
                        $image.cropper = new Cropper(cropperElement, {
                            viewMode: 1,
                            checkOrientation: false,
                            autoCrop: true,
                            autoCropArea: 1,
                            strict: true,
                            movable: false,
                            zoomable: false,
                            restore: false,
                            ready: function (e) {
                                croppStartingData = $image.cropper.getData(true);
                                options.cropperRotateBtnSelector.prop("disabled", false);
                            },
                            cropstart: function (e) {
                                that._trigger('modalinprogessstatus', e, true);
                            },
                            crop: function (e) {
                            },
                            cropend: function (e) {
                                const currentData = $image.cropper.getData(true),
                                  cropNotChanged = JSON.stringify(croppStartingData) === JSON.stringify(currentData);
                                options.cropperStatusBtnSelector.prop("disabled", cropNotChanged);
                                that._trigger('modalinprogessstatus', e, !cropNotChanged);
                            }
                        });

                    })
                    .on('hidden.bs.modal', function (e) {
                        that._trigger('modalinprogessstatus', e, false);
                        that._trigger("modalhiddenevent", e, true);
                        $image.cropper.destroy();
                        $(this).attr("data-new", false);
                        options.cropperButtonSelector.prop("disabled", false);
                        options.cropperStatusBtnSelector
                            .prop("disabled", true);
                        options.cropperResultMessageBoxSelector
                            .empty()
                            .end()
                            .active = false;
                    })
                    .on('show.bs.modal', function (e) {
                        that._trigger("modalshowevent", e, true);
                    })
                    .on('hide.bs.modal', function (e) {
                        that._trigger("modalhideevent", e, true);
                    });

                options.cropperButtonDivSelector.on(
                    'click',
                    '[data-method]',
                    function (e) {
                        const data = $.extend({}, $(this).data()); // Clone
                        if (data.method === "rotate") {
                            const contData = $image.cropper.getContainerData();
                            $image.cropper.setCropBoxData({
                                width: 2,
                                height: 2,
                                top: (contData.height / 2) - 1,
                                left: (contData.width / 2) - 1
                            });
                        }
                        else if (data.method === "commit") {
                            if (editType === "download") {
                                data.method = "getData";
                                data.option = true;
                            }
                            else if (editType === "upload") {
                                data.method = "getCroppedCanvas";
                            }
                        }

                        that._trigger('modalinprogessstatus', e, true);

                        const result = $image.cropper[data.method](data.option);

                        switch (data.method) {
                            case 'scaleX':
                            case 'scaleY':
                                $(this).data('option', -data.option);
                                break;
                            case 'reset':
                                options.cropperButtonSelector.prop("disabled", false);
                                options.cropperStatusBtnSelector.prop("disabled", true);
                                break;
                            case 'getData':
                                if (result && $image.submitData) {
                                    $image.submitData(result);
                                }
                                break;
                            case 'getCroppedCanvas':
                                if (result && $image.processCroppedCanvas) {
                                    $image.processCroppedCanvas(result);
                                }
                                break;
                            case 'rotate':
                                if (result && $image.rotateCanvas) {
                                    $image.rotateCanvas();
                                }
                                break;
                        }

                        const currentData = $image.cropper.getData(true);

                        if (JSON.stringify(croppStartingData) === JSON.stringify(currentData))
                        {options.cropperStatusBtnSelector.prop("disabled", true);
                        that._trigger('modalinprogessstatus', e, false);}

                    });
            },

            _initEditModal: function(){
                this._initEditModalId();
                this._initEditModalImgId();
                this._initCropperResultMessageBoxSelector();
                this._initCropperButtonDivSelector();
                this._initCropperButtonSelector();
                this._initCropperStatusBtnSelector();
                this._initCropperRotateBtnSelector();
                this._initEditModalEventHandler();
            },

           _initStatusDataName: function () {
                const options = this.options;
                if (options.statusDataName === undefined) {
                    options.statusDataName = "file-pk";
                }
            },

            _initSortable: function() {
                const options = this.options,
                  that = this,
                  defaultSortableOptions = {
                      disabled: false,
                      delay: 300,
                      animation: 200,
                      touchStartThreshold: 5,
                      ghostClass: "galleryWidget-sortable-ghost",
                      chosenClass: "galleryWidget-sortable-chosen",
                      filter: ".btn, .toggle, img, a, span, progress",
                  };

                const sortableOptions = $.extend(defaultSortableOptions, options.sortableOptions || {});
                delete sortableOptions.handle;

                sortableOptions.onUpdate = function (evt) {
                    that._trigger("sortableUpdate", evt.item);
                }

                Sortable.create(options.filesContainer.get(0), sortableOptions)
            },

            _initFilesDataToInputDataFunction: function () {
                const options = this.options;
                if (options.filesDataToInputDataFunction === undefined) {
                    options.filesDataToInputDataFunction = function(filesData) {return filesData};
                }
            },

            _initSpecialOptions: function () {
                this._super();
                this._initStatusDataName();
                this._initSortable();
                this._initEditModal();
                this._initWidgetHiddenInput();
                this._initFilesDataToInputDataFunction();
            },

            _initWidgetHiddenInput: function () {
                const options = this.options;
                if (options.hiddenFileInput === undefined) {
                    // todo: how to find the input?
                } else if (!(options.hiddenFileInput instanceof $)) {
                    options.hiddenFileInput = $(options.hiddenFileInput);
                }
            },

        }
    );
});
