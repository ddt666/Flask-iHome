function hrefBack() {
    history.go(-1);
}


$(document).ready(function () {
    //获取详情页面要展示的房屋编号
    var queryData = decodeQuery();
    var houseId = queryData["id"];

    // 获取该房屋的详细信息
    $.get(window.serv + "/houses/" + houseId, function (resp) {
        if (resp.errno === "0") {
            $(".swiper-container").html(template("house_image_tmpl", {
                img_urls: resp.data.house.img_urls,
                price: resp.data.house.price
            }));
            $(".detail-con").html(template("house_detail_tmpl", {house: resp.data.house}));

            // resp.user_id为访问页面用户，resp.data.user_id为房东页面
            if (resp.data.user_id != resp.data.house.user_id) {
                $(".book-house").attr("href", "/booking.html?hid=" + resp.data.house.hid)
                $(".book-house").show();
            }


            var mySwiper = new Swiper('.swiper-container', {
                loop: true,
                autoplay: 2000,
                autoplayDisableOnInteraction: false,
                pagination: '.swiper-pagination',
                paginationType: 'fraction'
            })
        }
    });


})