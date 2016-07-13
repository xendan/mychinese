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
    
    function on_lesson_loaded(lesson_json) {
        $("#date").html("Date:" + new Date(last_lesson.date).toLocaleDateString("en-US")); 
        rest_get("dialog", lesson_json.dialog ,function(dialog_json) {
            if (dialog_json.link) {
                
            } else {
                var link = $("<input type='text'/>");
                $("#dialog").append(link).bind('paste', function(event) {
                    setTimeout( function() {
                        console.log("ok save " + link.val() );
                     }, 100);
                 });
            }
        });
    }

    function start_new_lesson(lesson_json) {
        var num = int($("#paid_num").text());
        num++;
        $("#paid_num").text(num);
        on_lesson_loaded(lesson_json);
    }

    function rest_get(name, id, handler) {
        $.ajax({
            url : "lessons/" + name + "/" + id,
            success : handler,
            error : handle_error
        });
    }

    $('#start_btn').click(function(){
        $.ajax({
            url : "lesson",
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
    if (last_lesson) {
        on_lesson_loaded(last_lesson);
    } else {
        $("#lesson").hide();
    }
 });
