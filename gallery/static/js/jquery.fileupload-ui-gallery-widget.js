(function ($, window, document, undefined) {
    'use strict';

    function get_cookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    $.widget(
        'blueimp.fileupload', $.blueimp.fileupload, {

            options: {
                before_submit: function (e, data) {
                    var $this = $(this),
                        that = $this.data('blueimp-fileupload') ||
                            $this.data('fileupload'),
                        options = that.options;

                    data.formData = {
                        "preview_size": options.previewMaxWidth,
                        "csrfmiddlewaretoken": get_cookie("csrftoken")
                    };
                },
            }

        })

})(jQuery, window, document);