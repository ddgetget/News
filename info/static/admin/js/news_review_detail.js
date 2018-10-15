function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {
    $(".news_review").submit(function (e) {
        e.preventDefault()

        // 新闻审核提交
        var params = {};
        // 获取到所有参数
        $(this).serializeArray().map(function (x) {
            params[x.name] = x.value;
        });

        // 取得参数得以判断
        var action = params['action'];
        var news_id = params['news_id'];
        var reason = params['reason'];

        if (action == "reject" && !reason) {
            return;
        }

        params = {
            'action': action,
            'news_id': news_id,
            'reason': reason
        }

        // 数据交互处理
        $.ajax({
            url: '/admin/news_review_detail',
            type: 'post',
            contentType: 'application/json',
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == '0') {
                    // 返回上一页
                    location.herf = document.referrer;
                } else {
                    alert(resp.errmsg);
                }
            }
        })
    })
})

// 点击取消，返回上一页
function cancel() {
    history.go(-1)
}