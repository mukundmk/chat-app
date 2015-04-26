$(document).ready(function(){
    active_id = null;
    public_keys = {};
    changed_time = "";
    loaded = [];
    $("#chat_nav").hide();
    $("#profile").hide();
    $("#name_nav").click(switch_to_profile);
    $("#chat_nav").click(switch_to_chat);
    $.get("/get_keys", set_keys);
    $.getJSON('/get_online', update_online);
    $("#search").typeahead({
        ajax: {
            url: '/search_user',
            valueField: 'value',
            displayField: 'label'
        },
        highlighter: function(item){
            return '<img src="/get_image?id='+item['value']+'" class="img img-circle" width="30" height="30"/>  '+item['label'];

        },
        render: function(items) {
            var that = this, display;

            items = $(items).map(function(i, item) {
                if (typeof item === 'object') {
                    display = item;

                    i = $(that.options.item).attr('data-value', item[that.options.valueField]);
                    i.find('a').html(that.highlighter(display));
                    return i[0];
                }
            });

            items.first().addClass('active');
            this.$menu.html(items);
            return this;
        },
        menu: '<ul class="typeahead dropdown-menu" style="width:200px"></ul>',
        onSelect: function(item){
            view_profile(item.value);
        },
        updater: function(item){
            return '';
        }
    });
});
function set_keys(result){
    var keys = JSON.parse(result);
    private_key = keys.privatekey;
    public_key = keys.publickey;
    var params = certParser(private_key);
    var key = pidCryptUtil.decodeBase64(params.b64);
    rsa_decrypt = new pidCrypt.RSA();
    var asn = pidCrypt.ASN1.decode(pidCryptUtil.toByteArray(key));
    var tree = asn.toHexTree();
    rsa_decrypt.setPrivateKeyFromASN(tree);
    params = certParser(public_key);
    key = pidCryptUtil.decodeBase64(params.b64);
    rsa_encrypt = new pidCrypt.RSA();
    asn = pidCrypt.ASN1.decode(pidCryptUtil.toByteArray(key));
    tree = asn.toHexTree();
    rsa_encrypt.setPublicKeyFromASN(tree);
    $.post("/update_publickey", {publickey: public_key});
    set_active(null);
    $.getJSON('/get_user', ready);
}
function ready(result){
    user=result;
    socket = io.connect('https://' + document.domain + ':' + location.port + '/chat');
    socket.on('connect', function(msg) {
        console.log(msg);
    });
    socket.on('receive message', function(msg) {
        if(msg.type == 'text') {
            var ciphertext = pidCryptUtil.decodeBase64(pidCryptUtil.stripLineFeeds(msg.data));
            var plaintext = rsa_decrypt.decrypt(pidCryptUtil.convertToHex(ciphertext));
            $("#messages_" + msg.from).append("<div class=\"bubble-container\"><div class=\"avatar avatar-left\"><img onclick=\"view_profile('" + msg.from + "')\" src=\"/get_image?id=" + msg.from + "\"/></div><div class=\"bubble bubble-left\">" + plaintext + "</div></div>");
        }
        else if(msg.type == 'image') {
            var plaintext = msg.data;
            $("#messages_" + msg.from).append("<div class=\"bubble-container\"><div class=\"avatar avatar-left\"><img onclick=\"view_profile('" + msg.from + "')\" src=\"/get_image?id=" + msg.from + "\"/></div><div class=\"bubble bubble-left\"><button class=\"btn btn-primary\" onclick=\"viewImage('" + plaintext + "')\">Image</button></div></div>");
        }
        else if(msg.type == 'video') {
            var plaintext = msg.data;
            $("#messages_" + msg.from).append("<div class=\"bubble-container\"><div class=\"avatar avatar-left\"><img onclick=\"view_profile('" + msg.from + "')\" src=\"/get_image?id=" + msg.from + "\"/></div><div class=\"bubble bubble-left\"><button class=\"btn btn-primary\" onclick=\"viewVideo('" + plaintext + "')\">Video</button></div></div>");
        }
    });
    $('#send').click(function(event) {
        var msg = {};
        var plaintext = $("#msg").val();
        if(plaintext=='')
            return;
        msg.to = active_id;
        msg.type = 'text';
        if(public_keys[msg.to]) {
            var params = certParser(public_keys[msg.to]);
            var key = pidCryptUtil.decodeBase64(params.b64);
            var rsa_encrypt2 = new pidCrypt.RSA();
            var asn = pidCrypt.ASN1.decode(pidCryptUtil.toByteArray(key));
            var tree = asn.toHexTree();
            rsa_encrypt2.setPublicKeyFromASN(tree);
            var crypted = rsa_encrypt2.encrypt(plaintext);
            var fromHex = pidCryptUtil.encodeBase64(pidCryptUtil.convertFromHex(crypted));
            msg.data_1 = pidCryptUtil.fragment(fromHex,64);
            crypted = rsa_encrypt.encrypt(plaintext);
            fromHex = pidCryptUtil.encodeBase64(pidCryptUtil.convertFromHex(crypted));
            msg.data_2 = pidCryptUtil.fragment(fromHex,64);
            $("#msg").val("");
            $("#messages_" + active_id).append("<div class=\"bubble-container\"><div class=\"avatar avatar-right\"><img class=\"my-img\" src=\"/get_image?id=" + user.id + "&time=" + changed_time + "\"/></div><div class=\"bubble bubble-right\" style=\"text-align:right\">" + plaintext + "</div></div>");
            socket.emit('send message', msg);
        }
    });
    $('#send_image').click(function(event){
        $("#image_file").trigger("click");
    });
    $('#send_video').click(function(event){
        $("#video_file").trigger("click");
    });
}

function send_image(event){
    var input = event.target;

    var reader = new FileReader();
    reader.onload = function(){
        var msg = {};
        var plaintext = reader.result;
        msg.to = active_id;
        msg.type = 'image';
        if(public_keys[msg.to]) {
            var params = certParser(public_keys[msg.to]);
            var key = pidCryptUtil.decodeBase64(params.b64);
            var rsa_encrypt2 = new pidCrypt.RSA();
            var asn = pidCrypt.ASN1.decode(pidCryptUtil.toByteArray(key));
            var tree = asn.toHexTree();
            rsa_encrypt2.setPublicKeyFromASN(tree);
            var crypted = rsa_encrypt2.encrypt(plaintext);
            var fromHex = pidCryptUtil.encodeBase64(pidCryptUtil.convertFromHex(crypted));
            msg.data_1 = pidCryptUtil.fragment(fromHex,64);
            crypted = rsa_encrypt.encrypt(plaintext);
            fromHex = pidCryptUtil.encodeBase64(pidCryptUtil.convertFromHex(crypted));
            msg.data_2 = pidCryptUtil.fragment(fromHex,64);
            $("#msg").val("");
            $("#messages_"+ active_id).append("<div class=\"bubble-container\"><div class=\"avatar avatar-right\"><img class=\"my-img\" src=\"/get_image?id=" + user.id + "&time=" + changed_time + "\"/></div><div class=\"bubble bubble-right\" style=\"text-align:right\"><button class=\"btn btn-primary\" onclick=\"viewImage2('"+plaintext+"')\">Image</button></div></div>");
            socket.emit('send message', msg);
        }
    };
    reader.readAsDataURL(input.files[0]);
}
function send_video(event){
    var input = event.target;

    var reader = new FileReader();
    reader.onload = function(){
        var msg = {};
        var plaintext = reader.result;
        msg.to = active_id;
        msg.type = 'video';
        if(public_keys[msg.to]) {
            var params = certParser(public_keys[msg.to]);
            var key = pidCryptUtil.decodeBase64(params.b64);
            var rsa_encrypt2 = new pidCrypt.RSA();
            var asn = pidCrypt.ASN1.decode(pidCryptUtil.toByteArray(key));
            var tree = asn.toHexTree();
            rsa_encrypt2.setPublicKeyFromASN(tree);
            var crypted = rsa_encrypt2.encrypt(plaintext);
            var fromHex = pidCryptUtil.encodeBase64(pidCryptUtil.convertFromHex(crypted));
            msg.data_1 = pidCryptUtil.fragment(fromHex,64);
            crypted = rsa_encrypt.encrypt(plaintext);
            fromHex = pidCryptUtil.encodeBase64(pidCryptUtil.convertFromHex(crypted));
            msg.data_2 = pidCryptUtil.fragment(fromHex,64);
            console.log(msg);
            socket.emit('send message', msg);
            $("#msg").val("");
            $("#messages_"+ active_id).append("<div class=\"bubble-container\"><div class=\"avatar avatar-right\"><img class=\"my-img\" src=\"/get_image?id=" + user.id + "&time=" + changed_time + "\"/></div><div class=\"bubble bubble-right\" style=\"text-align:right\"><button class=\"btn btn-primary\" onclick=\"viewVideo2('"+plaintext+"')\">Video</button></div></div>");
        }
    };
    reader.readAsDataURL(input.files[0]);
}

function viewImage(imgsrcid){
    $.ajax('/get_media_file?id='+imgsrcid,{
        cache: true,
        success: function(result){
            var ciphertext = pidCryptUtil.decodeBase64(pidCryptUtil.stripLineFeeds(result));
            var plaintext = rsa_decrypt.decrypt(pidCryptUtil.convertToHex(ciphertext));
            $("#show_img").attr("src",plaintext);
            $("#image_modal").modal();
        }
    });
}

function viewImage2(imgsrc){
    $("#show_img").attr("src",imgsrc);
    $("#image_modal").modal();
}

function viewVideo(vidsrcid){
    $.ajax('/get_media_file?id='+vidsrcid,{
        cache: true,
        success: function(result){
            var ciphertext = pidCryptUtil.decodeBase64(pidCryptUtil.stripLineFeeds(result));
            var plaintext = rsa_decrypt.decrypt(pidCryptUtil.convertToHex(ciphertext));
            var source = document.createElement('source');
            $(source).attr({
                'type':'video/mp4',
                'src': plaintext
            });
            $("#show_vid").append(source);
            $("#video_modal").modal();
        }
    });
}

function viewVideo2(vidsrc){
    var source = document.createElement('source');
    $(source).attr({
        'type':'video/mp4',
        'src': vidsrc
    });
    $("#show_vid").append(source);
    $("#video_modal").modal();
}

function update_online(result){
    for(var i in result){
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
        if(!public_keys[id]){
            $("#submit").attr("disabled");
            $.getJSON("/get_publickey?id="+id,function(result){
                public_keys[result["id"]]=result["key"];
                $("#submit").removeAttr("disabled");
            });
        };
        $("#sidebar_"+current_id).removeAttr("class");
        $("#sidebar_"+id).attr("class","active");
        $("#messages_"+current_id).hide();
        $("#messages_"+id).show();
    }
    else if(id == null && $("#sidebar").children().length>0){
        active_id = $($("#sidebar").children()[0]).attr("id").split("_")[1];
        id = $($("#sidebar").children()[0]).attr("id").split("_")[1];
        if(!public_keys[id]){
            $("#submit").attr("disabled");
            $.getJSON("/get_publickey?id="+id,function(result){
                public_keys[result["id"]]=result["key"];
                $("#submit").removeAttr("disabled");
            });
        };
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
                if(result["data"][i][1]=='text'){
                    var ciphertext = pidCryptUtil.decodeBase64(pidCryptUtil.stripLineFeeds(result["data"][i][2]));
                    var plaintext = rsa_decrypt.decrypt(pidCryptUtil.convertToHex(ciphertext));
                    console.log('h');
                    console.log(plaintext);
                }
                else
                    var plaintext = result["data"][i][2];
                if(result["data"][i][0]==id1){
                    if(result["data"][i][1]=='text')
                        text+="<div class=\"bubble-container\"><div class=\"avatar avatar-right\"><img class=\"my-img\" src=\"/get_image?id="+result["data"][i][0]+"&time="+changed_time+"\"/></div><div class=\"bubble bubble-right\" style=\"text-align:right\">"+plaintext+"</div></div>";
                    else if(result["data"][i][1]=='image')
                        text+="<div class=\"bubble-container\"><div class=\"avatar avatar-right\"><img class=\"my-img\" src=\"/get_image?id="+result["data"][i][0]+"&time="+changed_time+"\"/></div><div class=\"bubble bubble-right\" style=\"text-align:right\"><button class=\"btn btn-primary\" onclick=\"viewImage('"+plaintext+"')\">Image</button></div></div>";
                    else if(result["data"][i][1]=='video')
                        text+="<div class=\"bubble-container\"><div class=\"avatar avatar-right\"><img class=\"my-img\" src=\"/get_image?id="+result["data"][i][0]+"&time="+changed_time+"\"/></div><div class=\"bubble bubble-right\" style=\"text-align:right\"><button class=\"btn btn-primary\" onclick=\"viewVideo('"+plaintext+"')\">Video</button></div></div>";
                }
                else if(result["data"][i][0]==id2){
                    if(result["data"][i][1]=='text')
                        text+="<div class=\"bubble-container\"><div class=\"avatar avatar-left\"><img onclick=\"view_profile('"+result["data"][i][0]+"')\" src=\"/get_image?id="+result["data"][i][0]+"\"/></div><div class=\"bubble bubble-left\">"+plaintext+"</div></div>";
                    else if(result["data"][i][1]=='image')
                        text+="<div class=\"bubble-container\"><div class=\"avatar avatar-left\"><img onclick=\"view_profile('"+result["data"][i][0]+"')\" src=\"/get_image?id="+result["data"][i][0]+"\"/></div><div class=\"bubble bubble-left\"><button class=\"btn btn-primary\" onclick=\"viewImage('"+plaintext+"')\">Image</button></div></div>";
                    else if(result["data"][i][1]=='video')
                        text+="<div class=\"bubble-container\"><div class=\"avatar avatar-left\"><img onclick=\"view_profile('"+result["data"][i][0]+"')\" src=\"/get_image?id="+result["data"][i][0]+"\"/></div><div class=\"bubble bubble-left\"><button class=\"btn btn-primary\" onclick=\"viewVideo('"+plaintext+"')\">Video</button></div></div>";
                }
            }
            $("#messages_"+id2).prepend(text);
            loaded.push(id2);
        });
    }
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
        switch(result["friendship"]){
            case "0":
                $("#modal_buttons").html("<button onclick=\"add_friend('"+result["id"]+"')\" class=\"btn btn-primary\">Add Friend</button>");
            break;
            case "1":
                $("#modal_buttons").html("<button onclick=\"add_friend('"+result["id"]+"')\" class=\"btn btn-info\">Confirm Friend</button><button onclick=\"decline_friend('"+result["id"]+"')\" class=\"btn btn-danger\">Decline Friend</button>");
            break;
            default:
                $("#modal_buttons").html("");
        }
        $("#profile_modal").modal();
    });
}
function add_friend(id){
    $.post("/add_friend",{id: id},function(result){
        $("#added_list").html("");
        var data=JSON.parse(result);
        var added=data["added"];
        if(added.length > 0){
            for(var i in added){
                $("#added_list").append("<li><a href=\"javascript:view_profile('"+added[i]["id"]+"')\"><img src=\"/get_image?id="+added[i]["id"]+"\" class=\"img img-circle\" width=\"30\" height=\"30\"/>  "+added[i]["name"]+"</a></li>");
            }
            $("#added_count").html(data.length);
        }
        else{
           $("#added_count").html("");
        }
        var users=data["users"];
        var current=undefined;
        for(var i in users){
            var temp=$("#sidebar_"+users[i]["id"])
            if(temp.length>0){
                current=temp;
                continue;
            }
            if(!current){
                $("#sidebar").prepend("<li id=\"sidebar_"+users[i]["id"]+"\" onclick=\"set_active('"+users[i]["id"]+"')\"><a href=\"#\"><i id=\"online_"+users[i]["id"]+"\" class=\"fa fa-circle\" style=\"color:green;visibility:hidden;\"></i>  "+users[i]["name"]+"<img src=\"/get_image?id="+users[i]["id"]+"\" class=\"img-circle\" style=\"float:right;height:30px;width:30px;position:relative;top:-5px;\"/></a></li>");
                $("#container").append("<div id=\"messages_"+users[i]["id"]+"\" style=\"display: none;\"></div>");
                current=$("#sidebar_"+users[i]["id"]);
            }
            else{
                current.after("<li id=\"sidebar_"+users[i]["id"]+"\" onclick=\"set_active('"+users[i]["id"]+"')\"><a href=\"#\"><i id=\"online_"+users[i]["id"]+"\" class=\"fa fa-circle\" style=\"color:green;visibility:hidden;\"></i>  "+users[i]["name"]+"<img src=\"/get_image?id="+users[i]["id"]+"\" class=\"img-circle\" style=\"float:right;height:30px;width:30px;position:relative;top:-5px;\"/></a></li>");
                $("#container").append("<div id=\"messages_"+users[i]["id"]+"\" style=\"display: none;\"></div>");
                current=$("#sidebar_"+users[i]["id"]);
            }
        }
        $("#profile_modal").modal('hide');
    });

}
function decline_friend(id){
    $.post("/decline_friend",{id: id},function(result){
        $("#added_list").html("");
        var data=JSON.parse(result);
        if(data.length > 0){
            for(var i in data){
                $("#added_list").append("<li><a href=\"javascript:view_profile('"+data[i]["id"]+"')\"><img src=\"/get_image?id="+data[i]["id"]+"\" class=\"img img-circle\" width=\"30\" height=\"30\"/>  "+data[i]["name"]+"</a></li>");
            }
            $("#added_count").html(data.length);
        }
        else{
           $("#added_count").html("");
        }
        $("#profile_modal").modal('hide');
    });
}