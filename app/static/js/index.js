$(document).ready(function(){
    active_id = null;
    changed_time = "";
    loaded = [];
    set_active(null);
    $("#chat_nav").hide();
    $("#profile").hide();
    $("#name_nav").click(switch_to_profile);
    $("#chat_nav").click(switch_to_chat);
    $.getJSON('/get_user', ready);
    $.getJSON('/get_online', update_online);
});
function ready(result){
    user=result;
    console.log(user);
    socket = io.connect('http://' + document.domain + ':' + location.port + '/chat');
    socket.on('connect', function(msg) {
        console.log(msg);
    });
    socket.on('receive message', function(msg) {
        $("#messages_"+msg.from).append("<div class=\"bubble-container\"><div class=\"avatar avatar-left\"><img onclick=\"view_profile('"+msg.from+"')\" src=\"/get_image?id="+msg.from+"\"/></div><div class=\"bubble bubble-left\">"+msg.data+"</div></div>");
    });
    $('#send').click(function(event) {
        msg = {};
        msg.from = user.id;
        msg.to = active_id;
        msg.data = $("#msg").val();
        $("#msg").val("");
        $("#messages_"+active_id).append("<div class=\"bubble-container\"><div class=\"avatar avatar-right\"><img class=\"my-img\" src=\"/get_image?id="+msg.from+"&time="+changed_time+"\"/></div><div class=\"bubble bubble-right\" style=\"text-align:right\">"+msg.data+"</div></div>");
        socket.emit('send message', msg);
    });
}
function update_online(result){
    console.log(result);
    for(var i in result){
        console.log(i);
        if(result[i]){
            if($("#online_"+i).css("visibility")=="hidden"){
                $("#online_"+i).css("visibility","visible");
            }
        }
        else{
            if($("#online_"+i).css("visibility")=="visible"){
                $("#online_"+i).css("visibility","hidden");
            }
        }
    }
    setTimeout(function(){$.getJSON('/get_online', update_online);},10000);
}
function set_active(id){
    var current_id = active_id;
    active_id = id;
    if(current_id != null){
        $("#sidebar_"+current_id).removeAttr("class");
        $("#sidebar_"+id).attr("class","active");
        $("#messages_"+current_id).hide();
        $("#messages_"+id).show();
    }
    else if(id == null){
        active_id = $($("#sidebar").children()[0]).attr("id").split("_")[1];
        id = $($("#sidebar").children()[0]).attr("id").split("_")[1];
        $($("#sidebar").children()[0]).attr("class","active")
        $($("#container").children()[0]).show();
    }
    if($.inArray(id, loaded)==-1){
        $.getJSON('/get_messages?id='+id, function(result){
            console.log(result);
            var id1 = result["id1"];
            var id2 = result["id2"];
            var text="";
            for(var i in result["data"]){
                if(result["data"][i][0]==id1){
                    text+="<div class=\"bubble-container\"><div class=\"avatar avatar-right\"><img class=\"my-img\" src=\"/get_image?id="+result["data"][i][0]+"&time="+changed_time+"\"/></div><div class=\"bubble bubble-right\" style=\"text-align:right\">"+result["data"][i][1]+"</div></div>";
                }
                else if(result["data"][i][0]==id2){
                    text+="<div class=\"bubble-container\"><div class=\"avatar avatar-left\"><img onclick=\"view_profile('"+result["data"][i][0]+"')\" src=\"/get_image?id="+result["data"][i][0]+"\"/></div><div class=\"bubble bubble-left\">"+result["data"][i][1]+"</div></div>";
                }
            }
            $("#messages_"+id2).prepend(text);
            loaded.push(id2);
        });
    }
    console.log(active_id);
}

function switch_to_profile(){

    $("#name_nav").fadeOut(function(){$("#chat_nav").fadeIn();});
    $("#chat").fadeOut(function(){$("#profile").fadeIn();});
    $.get("/get_profile", function(result){
        $("#profile").html(result);
    });
}
function switch_to_chat(){
    if(image_changed){
        $(".my-img").each(function(){this.src = "/get_image?id="+user.id+"&time="+changed_time;})
    }
    $("#chat_nav").fadeOut(function(){$("#name_nav").fadeIn();});
    $("#profile").fadeOut(function(){$("#chat").fadeIn();});
}

function view_profile(id){
    $.getJSON("/profile_of?id="+id, function(result){
        $("#modal_img").attr("src","/get_image?id="+result["id"]);
        $("#modal_title").html(result["name"]);
        $("#modal_email").html(result["email"]);
        $("#modal_status").html(result["status"]);
        $("#profile_modal").modal();
    });
}