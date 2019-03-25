$(function(){
    //画像ファイルプレビュー表示のイベント追加 fileを選択時に発火するイベントを登録
    $('form').on('change', 'input[type="file"]', function(e) {
        var file = e.target.files[0],
            reader = new FileReader(),
            $preview = $(".preview");
            t = this;
        

        // 画像ファイル以外の場合は何もしない
        if(file.type.indexOf("image") < 0){
        return false;
        }

        // ファイル読み込みが完了した際のイベント登録
        reader.onload = (function(file) {
            return function(e) {
                //既存のプレビューを削除
                $preview.empty();
                // .prevewの領域の中にロードした画像を表示するimageタグを追加
                $preview.attr({
                    src: e.target.result,
                    class: "preview",
                    title: file.name
                });
                //delete_imgのcheckboxをoffにする
                //ボタンを非active状態にする
                $('.delete_img').prop('checked',false);
                $('#check-label').attr('class','btn btn-warning')
            };
        })(file);

        reader.readAsDataURL(file);
    });
});