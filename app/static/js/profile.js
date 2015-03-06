image_changed = false;
function edit(item){
    $("#input_"+item).val($("#static_"+item).html());
    $("#static_"+item+", #button_static_"+item).fadeOut(function(){$("#edit_"+item+", #button_edit_"+item).fadeIn();});

}
function cancel(item){
    $("#edit_"+item+", #button_edit_"+item).fadeOut(function(){$("#static_"+item+", #button_static_"+item).fadeIn();});
}
function change(item){
    if($("#input_"+item).val()!=$("#static_"+item).html()){
        $.post('/edit_profile', { key: item, value: $("#input_"+item).val() }, function(result){
            r=result.split(":");
            $("#static_"+r[0]).html(r[1]);
        });
    }
    cancel(item);
}
function change_image(){
    $("#file").trigger("click");
}

function upload_image(){
    var fd = new FormData($("#upload_form")[0]);
    $.ajax({
        url: "/upload_image",
        type: "POST",
        data: fd,
        enctype: "multipart/form-data",
        processData: false,
        contentType: false,
        success: function(result){
            changed_time = new Date().toUTCString();
            $("#image").attr("src","/get_image?id="+result+"&time="+changed_time);
            image_changed = true;
        }
    });
    $("#file").val("");
}