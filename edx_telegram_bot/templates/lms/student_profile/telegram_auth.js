<%!
from django.utils.translation import ugettext as _
from django.conf import settings
%>
var get_token = $('.telegram-auth .telegram-get-token');
function getToken(type) {
    var url = "/api/bot/generate/",
        data = {'id': '${user.id}'};
    $.ajax({
        url: url,
        data: data,
        csrf: '${ csrf_token }',
        type: type
    }).success(function (data) {
        var url = "https://telegram.me/${settings.TELEGRAM_BOT.get('bot_name')}?start="+data.token;
        window.open(url);
    }).error(function (jqXHR, textStatus, errorThrown) {
        console.log(textStatus, errorThrown);
        alert(errorThrown);
    });
}
get_token.on('click', function () {
    getToken("POST");
});
