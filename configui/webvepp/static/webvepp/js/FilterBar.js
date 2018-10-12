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
        var path = location.pathname.split('/');
        var startname = path[3];
        settings = (data["filter_buttons"]===undefined)? undefined: jQuery.extend(true,[],data["filter_buttons"]);
        if(settings!=undefined){
            drawButtons();
        }
        if(startname!=""){
            $(document).trigger("find_object",startname);
        }
        else{
            if(settings==undefined){
                $(document).trigger("reload_tree",null);
            }
            else{
                $("#Filter_bar li:first-child").trigger("click");
            }
        }
    };

    function processFoundData(found_data){
        if(found_data["reload"]=="true"){
            var path = location.pathname.split('/');
            goToPage(path[2]);
        }
        else{
            if(found_data["filter_name"] != null){
                $("#filter_"+found_data["filter_name"]).trigger("click");
            }
            else{
                $(document).trigger("tree_created");
    	    }
            /*$("#filter_"+found_data["filter_name"]).addClass("active");
            $(document).trigger("tree_created");*/
        }
    };

    $(document).on("settings_loaded",function(event,settings_data){
        setSettings(settings_data);
    });

    $(document).on("object_found",function(event,found_data){
        processFoundData(found_data);
    });

    return {

    }
};

goToPage = function(address){
    document.location.href = WEBVEPP.serveradr() + 'webvepp/'+address;
};
