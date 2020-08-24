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
})