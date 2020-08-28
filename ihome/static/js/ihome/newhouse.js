$(document).ready(function () {
    // 向后端获取城区信息
    $.get(window.serv + "/areas", function (resp) {
        if (resp.errno === "0") {
            var areas = resp.data;
            // for(var i=0;i<areas.length;i++){
            //     $("#area-id").append('<option value="'+areas[i].area_id+'">'+areas[i].name+'</option>')
            // }


            // 使用js模板
            var html = template("areas-tmpl", {areas: areas});
            //console.log(html)

            $("#area-id").html(html);
        } else {
            alert(resp.errmsg)
        }
    }, "json");

    $("#form-house-info").submit(function (e) {
        e.preventDefault();

        // 处理表单数据
        var data = {};
        $("#form-house-info").serializeArray().map(function (x) {
            data[x.name] = x.value;
        });

        //收集设施id信息
        var facility = [];
        $(":checked[name=facility]").each(function (i, x) {
            facility[i] = $(x).val();
        });
        data.facility = facility;

        //想后端发送请求
        $.ajax({
            url: window.serv + "/houses/info",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(data),
            dataType: "json",
            headers: {
                "X-CSRFTOKEN": getCookie("csrf_token")
            },
            success: function (resp) {

                console.log(resp.errno);
                if (resp.errno === "4101") {
                    //用户未登录
                    location.href = "/login.html"
                } else if (resp.errno === "0") {
                    alert("添加成功");
                    // 隐藏基本信息表单
                    $("#form-house-info").hide();
                    // 显示图片表单
                    $("#form-house-image").show();
                    // 设置图片表单中house_id
                    $("#house-id").val(resp.data.house_id)

                } else {
                    alert(resp.errmsg)
                }
            }

        })
    });

    //
    $("#form-house-image").submit(function (e) {
        e.preventDefault()

        $(this).ajaxSubmit({
            url: window.serv + "/houses/image",
            type: "post",
            dataType: "json",
            headers: {
                "X-CSRFTOKEN": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno === "4101") {
                    //用户未登录
                    location.href = "/login.html"
                } else if (resp.errno === "0") {
                    $(".house-image-cons").append('<img src="'+resp.data.image_url+'">');

                } else {
                    alert(resp.errmsg)
                }
            }
        })
    })
});

