function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

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
    }, "json")
})