<%!
from django.utils.translation import ugettext as _
from django.conf import settings
%>
var block = $('.telegram-auth .token-block'),
    get_token = $('.telegram-auth .telegram-get-token'),
    loader = $('.telegram-auth .djdt-loader'),
    reset_token = $('.telegram-auth .token-reset'),
    success_text = "";
function getToken(type) {
    block.hide();
    get_token.hide();
    loader.hide();
    var url = "/api/bot/generate/",
        data = {};
    if (type == "GET") {
        url = url + "?id=${user.id}";
    } else {
        data = {'id': '${user.id}'};
        if(type== "POST"){
            success_text = "${_('Token has been created')}"
        } else if(type=="PUT"){
            success_text = "${_('Token has been updated')}"
        }
    }
    $.ajax({
        url: url,
        data: data,
        csrf: '${ csrf_token }',
        type: type
    }).success(function (data) {
        loader.hide();
        if (data.token) {
            $('.telegram-auth .telegram-token')
                .attr('href',"https://telegram.me/${settings.TELEGRAM_BOT.get('bot_name')}?start="+data.token);
            block.show();
            $(".telegram-success").text(success_text).show().fadeOut(2000);
        } else {
            get_token.show();
        }
    }).error(function (jqXHR, textStatus, errorThrown) {
        console.log(textStatus, errorThrown);
        loader.hide();
        get_token.show();
        alert(errorThrown);
    });
}
get_token.on('click', function () {
    getToken("POST");
});
reset_token.on('click', function () {
    if (confirm('${_("Are you really want to generate new token?")}')) {
        getToken("PUT");
    }
    return false;

})

getToken("GET");