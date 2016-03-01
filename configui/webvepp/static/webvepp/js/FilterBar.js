WEBVEPP.namespace("WEBVEPP.FilterBar");
WEBVEPP.FilterBar = function(){
    var settings,
        filters = d3.select("#Filter_bar");

    function checkActive(){
        var address = location.pathname.split('/')[2];
        if(address == "") address = "camacs";
        $("#menu_"+address).addClass("active");
    };

    function drawButtons(){
        var buttons = filters.selectAll("li")
            .data(settings);
        var button = buttons.enter();
        button.append("li");

        var button_update = buttons;

        button_update
            .on('click', function(d){
               $(document).trigger("reload_tree",d.name);
            })
            .text(function(d) {
                if(d.name)
                    return d.name;
            });

        button_remove = buttons.exit()
            .remove();
    };

    function setSettings(data){
        if(!data.filter_buttons)
            return;
        settings = (data["filter_buttons"]===undefined)? undefined: jQuery.extend(true,[],data["filter_buttons"]);
        drawButtons();
    };

    $(document).on("settings_loaded",function(event,settings_data){
        setSettings(settings_data);
    });

    return {
    }
};

goToPage = function(address){
    document.location.href = WEBVEPP.serveradr() + 'webvepp/'+address;
};