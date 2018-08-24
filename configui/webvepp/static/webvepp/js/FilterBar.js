WEBVEPP.namespace("WEBVEPP.FilterBar");
WEBVEPP.FilterBar = function(){
    var settings,
        filters = d3.select("#Filter_bar");

    function checkActive(name){
        filters.selectAll("li").classed("active",false);
        $("#filter_"+name).addClass("active");
    };

    function drawButtons(){
        var buttons = filters.selectAll("li")
            .data(settings);
        var button = buttons.enter();
        button.append("li")
            .attr("id",function(d){
                return "filter_"+d.name;
            });

        var button_update = buttons;

        button_update
            .on('click', function(d){
                checkActive(d.name)
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
        //console.log(data);
        settings = (data["filter_buttons"]===undefined)? undefined: jQuery.extend(true,[],data["filter_buttons"]);
        if(settings==undefined){
            $(document).trigger("reload_tree",null);
            return;
        }
        drawButtons();
        $("#Filter_bar li:first-child").trigger("click");
        //$("#Filter_bar li:first-child").addClass("active");
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