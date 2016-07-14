$(document).ready(function() {
    function getCookie(name) {
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

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
         return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
       beforeSend: function(xhr, settings) {
           if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
               xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });

    function handle_error(xhr, errmsg, err) {
        console.log(xhr.status + ": " + xhr.responseText);
    }

    function update_lesson_num(json) {
        $("#paid_num").text(json.lesson_num)
    }

    function on_dialog_loaded(dialog_json) {
        function append_to_dialog_div(name) {
            var link = $("<input id='dialog_" + name + "_inp' type='text'/>");
            $("#dialog").append(link).bind('input', function(event) {
                    setTimeout( function() {
                        dialog_json.fields[name] = link.val();
                        rest_put("dialog", dialog_json, on_dialog_loaded);
                     }, 100);
            });
        }

        if (dialog_json.fields.link) {
            $("#dialog_link_inp").remove();
            var dialog_href = $("<a target='_blank'  href='" + dialog_json.fields.link + "'></a>");
            var has_name = false;
            if (dialog_json.fields.name) {
                dialog_href.html(dialog_json.fields.name);
                has_name = true;
            }
            $("#dialog").append(dialog_href);
            if (!has_name) {
                append_to_dialog_div('name')
                $(dialog_href).html("Dialog link");
            }

        } else {
            append_to_dialog_div('link');
        }
    }
    
    function on_lesson_loaded(lesson_json) {
        $("#date").html("Date:" + new Date(last_lesson.fields.date).toLocaleDateString("en-US"));
        rest_get("dialog", lesson_json.fields.dialog, on_dialog_loaded);
    }

    function start_new_lesson(lesson_json) {
        var num = parseInt($("#paid_num").text());
        num--;
        $("#paid_num").text(num);
        on_lesson_loaded(lesson_json);
    }

    var rest_root = "lessons/";

    function rest_get(name, id, handler) {
        $.ajax({
            url : rest_root + name + "/" + id,
            success : handler,
            error : handle_error
        });
    }

    function rest_put(name, obj, handler) {
        $.ajax({
            url : rest_root + name,
            success : handler,
            type : "PUT",
            data : JSON.stringify([obj]),
            error : handle_error
        });
    }


    $('#start_btn').click(function(){
        $.ajax({
            url : "lessons/lesson",
            type : "POST",
            success : start_new_lesson,
            error : handle_error
        })
    });
    $('#pay_form').on('submit', function(event){
        event.preventDefault();
        $.ajax({
            url : "pay_lessons",
            type : "POST",
            data: $("#pay_form").serialize(),
            success : update_lesson_num,
            error: handle_error
        });
    });
    if (typeof last_lesson !== 'undefined') {
        on_lesson_loaded(last_lesson);
    } else {
        $("#lesson").hide();
    }
 });
