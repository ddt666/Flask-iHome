function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}

$(document).ready(function () {

    $("#form-avatar").submit(function (e) {
        // 阻止表单的默认行为
        e.preventDefault();
        // 利用jquery.form.min.js提供的ajaxSubmit对表单进行异步提交
        $(this).ajaxSubmit({
            url: "/api/v1.0/users/avatar",
            type: "post",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno === "0") {
                    // 上传成功

                    var avatarUrl = resp.data.avatar_url;
                    $("#user-avatar").attr("src", avatarUrl)
                } else {
                    alert(resp.errmsg)
                }
            }

        })

    })


    $("#form-name").submit(function (e) {
        // 阻止表单的默认行为
        e.preventDefault();
        var name = $("#user-name").val();

        if (!name) {
            $("#error-msg span").html("请填写用户名");
            $("#error-msg").show();
            return;
        }

        var data = {name: name};
        var jsonData = JSON.stringify(data);
        $.ajax({
            url: "/api/v1.0/users/name",
            type: "put",
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: jsonData,
            success: function (resp) {
                if (resp.errno === "0") {
                    // 保存成功

                    location.href = "/my.html"
                } else {
                    alert(resp.errmsg)
                }
            }

        });


    })
});
