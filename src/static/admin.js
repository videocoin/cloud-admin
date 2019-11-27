jQuery(document).ready(function($) {
    $(function() {
      $("#events-table").tablesorter();
    });
    $('.validate').click(function(e) {
        var button = $(this);
        button.attr("disabled", true);
        $('.validate_loading').show();
        $.get({
            url: button.attr('data-url'),
            contentType : 'application/json',
        }).done(function(data) {
            button.attr("disabled", false);
            $('.validate_loading').hide();
            var result_html = ''
            for (key in data) {
                result_html += '<h3>'+key+'</h3>'
                result_html += '<div>'
                result_html += '<span><b>Description: </b> </span><span>'+ data[key]['description'] +'</span>'
                result_html += '<hr>'
                if (data[key]['is_valid']) {
                    result_html += '<span><b>Is valid: </b> </span><span style="color:green">'+ data[key]['is_valid'] +'</span>'
                } else {
                    result_html += '<span><b>Is valid: </b> </span><span style="color:#a41515">'+ data[key]['is_valid'] +'</span>'
                }
                result_html += '<hr>'
                result_html += '<div style="padding-left: 30px;">'
                for (k in data[key]['errors']) {
                    result_html += '<span>'+ data[key]['errors'][k] +'</span><hr>'
                }
                result_html += '</div>'
                result_html += '</div>'
            }
            $('.validate_result').html(result_html)
        }).fail(function() {
            button.attr("disabled", false);
            $('.validate_loading').hide();

        });
        e.preventDefault();

    });

});
