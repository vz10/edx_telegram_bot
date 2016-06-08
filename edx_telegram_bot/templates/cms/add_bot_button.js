<%!
from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.sites.models import Site
%>

var add_button = $('.add-bot'),
	remove_button = $('.remove-bot');
	no_bot = '${_("Bot is not connected to your course")}';
// block = $('.add-bot'),
//     get_token = $('.telegram-auth .telegram-get-token'),
//     loader = $('.telegram-auth .djdt-loader'),
//     reset_token = $('.telegram-auth .token-reset'),
//     success_text = "";

function check_course(method){
    var url = "/bot/api/bot_course/";
    var data = window.location.pathname;
 	$.ajax({
        // url: 'http://127.0.0.1:8000' + url,
        url: '${Site.objects.get_current()}' + url,
        data: {key: data},
        type: method,
        csrf: '${ csrf_token }',
    }).success(function (data) {
    	if (data.bot) {
    		remove_button.show();add_button.hide();
    		var bot_title = $('#bot-title'),
				bot_info = $('#bot-info'),
				bot_link = $('#bot-link');
			var link_to_bot = 'https://telegram.me/'+data.bot_name
    		bot_info.text('${_("Bot for this course is @")}'+data.bot_name);
    		bot_link.html('<p><h5>Link to bot:</h5><a href="'+link_to_bot+'" target="blank">'+link_to_bot+'</a></p>');
    	}
    	else {
	 		var bot_title = $('#bot-title'),
				bot_info = $('#bot-info'),
				bot_link = $('#bot-link');
    		add_button.show();remove_button.hide();
    		bot_info.text(no_bot);
    		bot_link.html('');
    	}
	}
    ).error(function (jqXHR, textStatus, errorThrown) {
        console.log(jqXHR, textStatus, errorThrown);
      
    });
}

add_button.on('click', function(e){
    e.preventDefault();
	check_course('POST');
});

remove_button.on('click', function(e){
    e.preventDefault();
	check_course('DELETE');
});
check_course('GET');
