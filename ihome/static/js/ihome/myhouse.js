$(document).ready(function(){
    //$(".auth-warn").show();

    // 只有实名认证后才能发布新房源
    $.get(window.serv+"/users/auth",function (resp) {
        if (resp.errno === "4101"){
            location.href = "/login.html"
        }else if(resp.errno === "0"){

            // 未认证的用户，在页面中展示“去认证”的按钮
            if (!(resp.data.real_name && resp.data.id_card)){
                $(".auth-warn").show();
                return
            }
            // 已认证的用户，请求其之前发布的房源信息
            $.get(window.serv+"/user/houses",function (resp) {
                if(resp.errno === "0"){
                    var html = template("houses-list-tmpl",{houses:resp.data})
                    $("#houses-list").append(html)
                }
            })

        }
    })
});