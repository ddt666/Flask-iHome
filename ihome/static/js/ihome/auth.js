function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}


$(document).ready(function (e) {

    $.get(window.serv + "/users/auth", function (resp) {
        if (resp.errno === "0") {
            if (resp.data.real_name && resp.data.id_card) {

                $("#real-name").val(resp.data.real_name);
                $("#id-card").val(resp.data.id_card);
                $("#real-name").prop("disabled", true);
                $("#id-card").prop("disabled", true);
                $("#form-auth>input[type=submit]").hide();

            }

        } else if (resp.errno === "4101") {
            location.href = "/login.html"
        } else {
            alert(resp.errmsg)
        }
    }, "json");

    $("#form-auth").submit(function (e) {
        e.preventDefault();

        var realName = $("#real-name").val();
        var idCard = $("#id-card").val();

        if (!realName) {
            $(".error-msg span").html("真实姓名不能为空");
            $(".error-msg").show();
            return
        }
        if (!idCard) {
            $(".error-msg span").html("身份证不能为空");
            $(".error-msg").show();
            return
        }

        var data = {
            real_name: realName,
            id_card: idCard
        };

        var jsonData = JSON.stringify(data);

        $.ajax({
            url: window.serv + "/users/auth",
            type: "post",
            contentType: "application/json",
            data: jsonData,
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno === "0") {
                    $(".error-msg").hide();
                    showSuccessMsg();
                    $("#real-name").prop("disabled", true);
                    $("#id-card").prop("disabled", true);
                    $("#form-auth>input[type=submit]").hide();

                }

            }
        })
    })


});