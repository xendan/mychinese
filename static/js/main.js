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
                        onValueChangedHandler(_self);
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
                        dialog_json[name] = link.val();
                        rest_update("PUT", "dialog", dialog_json, on_dialog_loaded);
                     }, 100);
            });
        }
        $("#dialog").html("");
        if (dialog_json.link) {
            var dialog_href = $("<a target='_blank'  href='" + dialog_json.link + "'></a>");
            var has_name = false;
            if (dialog_json.name) {
                dialog_href.html(dialog_json.name);
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
                    if (!word.hasOwnProperty("id")) {
                        append_empty_word();
                        append_delete_link($("#new_word_row"));

                    }
                    word.id = new_word.id;
                }
                function append_delete_link(li) {
                    li.append($("<a href='#'>X</a>").click(function() {
                        rest_delete("word", word.id, function() {
                            $("#word_row" + word.id).remove();
                        });
                        li.attr("id", "word_row" + word.id);
                        return false;
                    }));
                }
                function create_word_element(name) {
                    var input = $("<input type='text' name='" + name + "' value='" + word[name] + "' />");
                    input.onDelayedInput(function(self) {
                        var type = word.hasOwnProperty("id") ? "POST" : "PUT";
                        word[name] = self.val();
                        rest_update(type, "word", word, on_word_updated);
                    });
                    return input;
                 }
                var form = $("<from></form>");
                all_fields.forEach(function(field) {
                    form.append(create_word_element(field))
                });
                var li = $("<li></li>").append(form);
                if (word.hasOwnProperty("id")) {
                    append_delete_link(li);
                } else {
                    li.attr("id", "new_word_row");
                }

                $("#words").append(li);
            }
            function append_empty_word() {
                var empty_word = {lesson:lesson_id};
                all_fields.forEach(function(field) {
                    empty_word[field] = "";
                });
                append_word(empty_word);
            }
            words.forEach(append_word);
            append_empty_word();
        }
    }

    function on_home_work_loaded(home_work_json) {
        $("#home_work").html("");
        var fields = {task: 'No Homework!', answer: 'Not done yet', correct: 'Not yet corrected'};
        var append = true;
        for (var name in fields) {
            var input = $( "input[value='" + name + "]" );
            if (append) {
                if (!input.length) {
                    input = $("<textarea name='" + name+ "' placeholder='"+ fields[name] + "' cols='50' rows='4' />")
                    $("#home_work").append(input);
                }
                input.val(home_work_json[name])
                .onDelayedInput(function(self) {
                    home_work_json[self.attr("name")] = self.val();
                    rest_update("POST", "home_work", home_work_json, on_home_work_loaded);
                });
                if (!home_work_json[name]) {
                    append = false;
                }
            } else {
                input.remove();
            }
        }
    }

    function on_lesson_loaded(lesson_json) {
        $("#date").html("Date:" + new Date(last_lesson.date).toLocaleDateString("en-US"));
        rest_get("dialog", lesson_json.dialog, on_dialog_loaded(lesson_json.id));
        rest_get("home_work", lesson_json.home_work, on_home_work_loaded);
        rest_search("note", lesson_json.id, on_notes_loaded(lesson_json.id));
        rest_search("word", lesson_json.id, on_words_loaded(lesson_json.id));

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

    function rest_delete(name, id, handler) {
        $.ajax({
            url : rest_root + name + "/" + id,
            success : handler,
            error : handle_error,
            type : "DELETE"
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
        //TODO make more rest
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
