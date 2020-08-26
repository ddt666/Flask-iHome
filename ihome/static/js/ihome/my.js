function logout() {

    $.ajax({
        url: "/api/v1.0/session",
        type: "delete",
        headers: {
            "X-CSRFTOKEN": getCookie("csrf_token")
        },
        dataType: "json",
        success: function (resp) {
            if (resp.errno === "0") {
                location.href = "/index.html"
            }
        }
    })
}

$(document).ready(function () {

    $.get("/api/v1.0/user", function (resp) {

        if (resp.errno === "0") {
            $("#user-avatar").attr("src", resp.data.avatar_url);
            $("#user-name").html(resp.data.name);
            $("#user-mobile").html(resp.data.mobile);
        } else if (resp.errno === "4101") {
            location.href = "/login.html"
        }
    })
})