$(document).ready(function showTweets(tweets){
    for (var tweet of  tweets ){
        $("#tweets").document.write('<li><b>'+tweet['tweet'] + '</b><br/>' +tweet['user'] + '  ' + tweet['timestamp']);
        $("#tweets").document.write('</li><br/>');
    }
});