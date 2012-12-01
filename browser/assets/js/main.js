var x1,y1,x2,y2

function update_labels(){
    $('#x1').html(x1)
    $('#x2').html(x2)
    $('#y1').html(y1)
    $('#y2').html(y2)
    $('#selection').show()
}

function init_draggables(){
    $( "#active_area" ).draggable({
        containment: "parent",
        drag: function(e){
            x1 =$('#active_area').offset().left - $('#img_holder img').offset().left
            y1 = $('#active_area').offset().top - $('#img_holder img').offset().top
            x2 = x1 + parseInt($('#active_area').css('width'), 10)
            y2 = y1 + parseInt($('#active_area').css('height'), 10)
            update_labels()
        }
    }).resizable({
        resize: function(e){
            x2 = x1 + parseInt($('#active_area').css('width'), 10)
            y2 = y1 + parseInt($('#active_area').css('height'), 10)
            update_labels()
        }
    });
}



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

    init_draggables()

    $('#img_holder img').live('mousedown', function(e){
        $('#active_area').css({
            left: e.offsetX + $('#img_holder img').offset().left + 'px',
            top: e.offsetY + $('#img_holder img').offset().top + 'px'
        }).show()

        x1 =$('#active_area').offset().left - $('#img_holder img').offset().left
        y1 = $('#active_area').offset().top - $('#img_holder img').offset().top
        x2 = x1 + parseInt($('#active_area').css('width'), 10)
        y2 = y1 + parseInt($('#active_area').css('height'), 10)

        update_labels()
    })

    $('#clear').on('click', function(){
        $('#selection').hide()
        $('#active_area').hide()
    })

    $('#search').on('click', function(){
        $('#results_inner').load('../../search/?' + $.param({
                                            p: $('#slider').slider("value"),
                                            x1: x1,
                                            x2: x2,
                                            y1: y1,
                                            y2: y2
                                    }))
        $('#results').show()
    })

    $( document ).tooltip({
        track: true
    });
});