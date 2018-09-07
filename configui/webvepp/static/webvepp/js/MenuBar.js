WEBVEPP.namespace("WEBVEPP.MenuBar");
WEBVEPP.MenuBar = function(menu_bar,settings){
    var menu_data,
        system_name = "";
    setSystemName();
    loadMenuData();

    //sets system_name from settings module
    function setSystemName(){
        system_name = settings.getSystemName();
    };

    //loads menu_data from server
    function loadMenuData(){
        $(document).trigger("set_loading_cursor");
        $.ajax({
            type: "GET",
            data: {system_name: JSON.stringify(system_name) },
            url: WEBVEPP.serveradr()+"webvepp/getMenuData",
            error: function(xhr, ajaxOptions, thrownError) {
                $(document).trigger("unset_loading_cursor");
                $(document).trigger("error_message",thrownError);
            },
            success: function(data){
                menu_data = data["buttons"];
                drawButtons();
                checkActive();
                $(document).trigger("menu_loaded",data);
                $(document).trigger("unset_loading_cursor");
            }
        });
    };

    //draws all menu buttons taken from menu_data
    function drawButtons(){
        var button = menu_bar.selectAll("li.button")
            .data(menu_data);
        var buttonEnter = button.enter().insert("li")
            .attr("class", "button")
            .attr("id",function(d){
                return "menu_"+d.link_name;
            })
            .append("a")
            .on('click', function(d){
                goToPage(d.link_name);
            })
            .text(function(d){
                return d.title;
            })

    };

    //depending on what page we are on highlights menu button
    function checkActive(){
        var address = location.pathname.split('/')[2];
        if(address == "")
            goToPage(menu_data[0].link_name);
        else
            menu_bar.select("#menu_"+address).attr("class", "active");
    };

    function getSampleName(sample_link){
        return $.grep(menu_data, function(e){ return e.link_name == sample_link; })[0].sample;
    };

    return {
        getSampleName: getSampleName
    }
};

goToPage = function(address){
    document.location.href = WEBVEPP.serveradr() + 'webvepp/'+address;
};