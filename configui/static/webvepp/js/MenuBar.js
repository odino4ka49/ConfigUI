WEBVEPP.namespace("WEBVEPP.MenuBar");
WEBVEPP.MenuBar = function(){
    checkActive();

    function checkActive(){
        var address = location.pathname.split('/')[2];
        if(address == "") address = "camacs";
        $("#menu_"+address).addClass("active");
    };

    return {
    }
};

goToPage = function(address){
    document.location.href = WEBVEPP.serveradr() + 'webvepp/'+address;
};