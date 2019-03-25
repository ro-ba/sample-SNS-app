$(function(){

    $('.delete_img').change(function() {
        //チェックの状態を取得
        var delete_img = $('.delete_img').prop('checked');
        
        if (delete_img) {
            before_src = $(".preview").attr('src');
            console.log(before_src);
            $('.preview').attr('src','../static/users/default.jpg');
        } else{
            console.log(before_src);
            $('.preview').attr('src',before_src );
        }
    });
});