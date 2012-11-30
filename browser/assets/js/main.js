function reload_img(){
    var param = ''
    if ($('input[name=surf]').attr('checked')){
        param = "?surf"
    }
    $('#ajax-box').load('../../frame/' + $('#slider').slider("value") + '/' + param)
}

$(document).ready(function() {
    values: [ 0,200 ],
    $("#slider").slider({
        value: parseInt($('#pos').html()),
        min: 0,
        max: parseInt($('#length').html()),
        step: 25,
        slide: function( event, ui ) {
            $('#pos').html(ui.value)
        },
        stop: function( event, ui ) {
            reload_img()
        }
    });

    $('[name=surf]').change(function() {
        reload_img()
    });
});