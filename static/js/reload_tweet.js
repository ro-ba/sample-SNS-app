$(function(){
    setInterval(function(){
        $.ajax({
            url:'/getTweet',
            type: 'POST',
            contentType: 'application/json;charset=UTF-8',
            cache: true,
        }).done(function(data){
            $('#count_tweets').html(data['count']['tweets']);
            $('#count_users').html(data['count']['users']);
            var newHtml = ''
            for (var tweet of  data['tweet'] ){
                newHtml = newHtml + '<div class="row bg-info"><div class="col-xs-2" style="padding-top:5%; padding-left:0%;"><a target="_top" href="/home?name='+ tweet['userID'] +'"><img class="img-circle col-md-offset-5 " width="60" height="60" src='+ tweet['img_url'] +' ></a></div>'
                newHtml = newHtml + '<div class="col-xs-10"><p class="h6" style="padding-top:5%;">'+tweet['tweet']+'</p><br/><p class="text-muted text-right">'+tweet['username']+'@'+tweet['userID'] + '  ' + tweet['timestamp'] 
                newHtml = newHtml + '</p></div></div>'
            }
            $('#write_tweets').html(newHtml);            
        }).fail(function(){
            console.log('fail');
        });
    },3000);
});