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

    (function($) {
          $.fn.onDelayedInput = function(onValueChangedHandler) {
            var _self = this;
            var timeout_is_on = false;
            this.bind('input', function(event) {
                function on_delay() {
                    if (value_old == _self.val()) {
                        timeout_is_on = false;
                        onValueChangedHandler(value_old);
                    } else {
                        setTimeout(on_delay, 500);
                    }
                    value_old = _self.val();
                }
                var value_old = _self.val();
                if (!timeout_is_on) {
                    timeout_is_on = true;
                    setTimeout(on_delay, 500);
                }
            });
            return this;
           }
      })(jQuery);

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
                        rest_update("PUT", "dialog", dialog_json, on_dialog_loaded);
                     }, 100);
            });
        }
        $("#dialog").html("");
        if (dialog_json.fields.link) {
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

    function on_notes_loaded(notes_arr) {

    }

    function on_words_loaded(lesson_id) {
        return function(words) {
            $("#words").html("");
            var all_fields = ["chinese", "pinyin", "translation"];
            function append_word(word) {
                function on_word_updated(new_word) {
                    if (!word.hasOwnProperty("pk")) {
                        apend_empty_word();
                    }
                    word.pk = new_word.pk;
                }

                function create_word_element(name) {
                    var input = $("<input type='text' name='" + name + "' value='" + word.fields[name] + "' />");
                    input.onDelayedInput(function(value) {
                        var type = word.hasOwnProperty("pk") ? "POST" : "PUT";    
                        word.fields[name] = value;
                        rest_update(type, "word", word, on_word_updated);
                    });
                    return input;
                 }
                var form = $("<from></form>");
                all_fields.forEach(function(field) {
                    form.append(create_word_element(field))
                });
                $("#words").append($("<li></li>").append(form));
            }
            function append_empty_word() {
                var fields = {lesson:lesson_id};
                all_fields.forEach(function(field) {
                    fields[field] = "";
                });
                var empty_word = {model:"lessons.word", fields:fields};
                append_word(empty_word);
            }
            append_empty_word();
            words.forEach(append_word);
        }
    }

    function on_lesson_loaded(lesson_json) {
        $("#date").html("Date:" + new Date(last_lesson.fields.date).toLocaleDateString("en-US"));
        rest_get("dialog", lesson_json.fields.dialog, on_dialog_loaded);
        rest_search("note", lesson_json.pk, on_notes_loaded)
        rest_search("word", lesson_json.pk, on_words_loaded(lesson_json.pk))
    }

    function start_new_lesson(lesson_json) {
        var num = parseInt($("#paid_num").text());
        num--;
        $("#paid_num").text(num);
        on_lesson_loaded(lesson_json);
    }

    var rest_root = "lessons/";

    function rest_search(name, lesson, handler) {
        $.ajax({
            url : rest_root + name,
            success : handler,
            error : handle_error,
            data : {lesson: lesson}
        });
    }

    function rest_get(name, id, handler) {
        $.ajax({
            url : rest_root + name + "/" + id,
            success : handler,
            error : handle_error
        });
    }

    function rest_update(type, name, obj, handler) {
        $.ajax({
            url : rest_root + name,
            success : handler,
            type : type,
            data : JSON.stringify(obj),
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
