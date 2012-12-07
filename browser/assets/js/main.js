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

function hide_selection(){
    $('#selection').hide()
    $('#active_area').hide()
}

function reload_img(){
    var param = ''
    if ($('input[name=surf]').attr('checked')){
        param = "?surf"
    }
    var frame_num = $('#slider').slider("value")
    $('#ajax-box').load('../../frame/' + frame_num + '/' + param, function(){
        $('.feature').css('background-color','#eeeeee')
        $('select option[value='+frame_num+']').parent().parent().css('background-color','#bbffbb')
    })
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
        hide_selection()
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

    $('#store').on('click', function(){
        var frame_num = $('#slider').slider("value")
        var el = $('<div class="content feature">                                  \
        <p>                                                               \
            <button class="append">Append/remove</button>                        \
            <span class="frame">'+frame_num+'</span>   \
            [<span class="x1">'+x1+'</span>, <span class="y1">'+y1+'</span>]  \
            [<span class="x2">'+x2+'</span>, <span class="y2">'+y2+'</span>]  \
            <button class="save">Save</button>       \
        </p>                                                              \
        <select name="frames" size="5">\
            <option value="'+frame_num+'">'+frame_num+'</option> \
        </select>         \
        </div>')

        $(el).appendTo("#features")
        var sel_height = $('select', el).height()

        var top_offset = $('.feature p').height() +
        parseInt($('.feature p').css('margin-top')) +
        parseInt($('.feature p').css('margin-bottom')) + 20

        $(el).css({
            height: Math.max((y2-y1), sel_height)+top_offset-20 + 'px',
            backgroundColor:'#bbffbb'
        })

        $('#img_holder img').clone()
            .css({
                position:'absolute',
                clip:'rect('+y1+'px '+x2+'px '+y2+'px '+x1+'px)',
                top: y1*-1+top_offset + 'px',
                left: x1*-1+20 + 150 +'px'
            }).appendTo(el)


        hide_selection()
        $(".ui-slider-handle").focus()
    })

    $('.append').live('click', function(e){
        var frame_num = $('#slider').slider("value")
        var el = $(this).parent().parent().find('select')
        if ($('option[value='+frame_num+']',el).length==0){
            $('<option value="'+frame_num+'">'+frame_num+'</option>').appendTo(el)
            $(this).parent().parent().css('background-color','#bbffbb')
        } else {
            $('option[value='+frame_num+']',el).remove()
            $(this).parent().parent().css('background-color','')
        }


        $(".ui-slider-handle").focus()
    })
    $('.save').live('click', function(){
        var fe = $(this).parent().parent()
        var frame_num = $('.frame', fe).html()
        var x1 = $('.x1', fe).html()
        var y1 = $('.y1', fe).html()
        var x2 = $('.x2', fe).html()
        var y2 = $('.y2', fe).html()

        frames=[]
        $('option', fe).each(function(i,e){
            frames.push($(e).attr('value'))
        })

        var box = $(this).parent().parent()

        $.ajax({
            type: 'POST',
            url: '../../save/',
            data: {
                frame_num:frame_num,
                x1:x1,
                y1:y1,
                x2:x2,
                y2:y2,
                frames:frames
            },
            success: function(){
                $(this).parent($(box).remove())
            }
        });
    })

});