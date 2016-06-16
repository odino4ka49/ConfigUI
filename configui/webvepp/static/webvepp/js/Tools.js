WEBVEPP.namespace("WEBVEPP.List");
WEBVEPP.List = function(tool_bar,settings){
    var list, list_settings,
        settings = settings,
        tool_data = [],
        scheme_names = {"system":"","sample":""},
        table = d3.select("body").select("table"),
        text_data = "";

    function setSchemeNames(tool_name){
        var pathname = location.pathname;
        var path = pathname.split('/');
        scheme_names.system = settings.getSystemName();
        if(path[1]=="webvepp"){
            if(path[2]=="tools"){
                scheme_names.sample = tool_name;
            }
            else
            {
                scheme_names.sample = "";
            }
        }
    };

    function loadListData(){
        $(document).trigger("set_loading_cursor");
        setWaitingText()
        $.ajax({
            type: "GET",
            data: {scheme_names: JSON.stringify(scheme_names) },
            url: WEBVEPP.serveradr()+"webvepp/getListData",
            error: function(xhr, ajaxOptions, thrownError) {
                $(document).trigger("unset_loading_cursor");
                $(document).trigger("error_message",thrownError);
            },
            success: function(data){
                list = data;
                drawListData();
                $(document).trigger("unset_loading_cursor");
                $(document).trigger("tree_created");
            }
        });
    };

    function loadListSettings(){
        $(document).trigger("set_loading_cursor");
        setWaitingText();
        $.ajax({
            type: "GET",
            data: {scheme_names: JSON.stringify(scheme_names) },
            url: WEBVEPP.serveradr()+"webvepp/getTreeSample",
            error: function(xhr, ajaxOptions, thrownError) {
                $(document).trigger("unset_loading_cursor");
                $(document).trigger("error_message",thrownError);
            },
            success: function(data){
                list_settings = data;
                $(document).trigger("unset_loading_cursor");
            }
        });
    };

    function loadValidationData(){
        $(document).trigger("set_loading_cursor");
        setWaitingText();
        $.ajax({
            type: "GET",
            data: {scheme_names: JSON.stringify(scheme_names) },
            url: WEBVEPP.serveradr()+"webvepp/getValidationData",
            error: function(xhr, ajaxOptions, thrownError) {
                $(document).trigger("unset_loading_cursor");
                $(document).trigger("error_message",thrownError);
            },
            success: function(data){
                text_data = data;
                drawTextData();
                $(document).trigger("unset_loading_cursor");
            }
        });
    };

    function setWaitingText(){
        text_data = "Wait for it...";
        drawTextData();
    }

    function drawTextData(){
        //text_data.replace(/\n/g, "<br />");
        table.select('thead').remove();
        table.select('tbody').remove();
        var thead = table.append('thead');
        var tbody = table.append('tbody');
        thead.append("tr").append("td").text(text_data);
    };

    function drawListData(){
        table.select('thead').remove();
        table.select('tbody').remove();
        var thead = table.append('thead');
        var tbody = table.append('tbody');
        thead.append("tr")
            .each(function(d,i){
                var row = d3.select(this);
                if(!list_settings) return;
                var attrs = list_settings.root.display_filter.min;
                if(list_settings.root.display_attributes.sort_type=="numbered"){
                    row.append("td").text("Index")
                }
                for(var j=0;j<attrs.length;j++){
                    var key = "";
                    if(typeof(attrs[j])=="string"){
                        key = attrs[j];
                    }
                    else if(typeof(attrs[j]=="object")){
                        key = attrs[j].key;
                    }
                    row.append("td").text(key);
                }
            })
        var row = tbody.selectAll("tr").data(list);
        var rowEnter = row.enter().append("tr")/*.append("td")
            .append('foreignObject')
            .append("xhtml:body")*/;

        var rowUpdate = row;
            rowUpdate.each(function(d,i){
                var row = d3.select(this);
                var attrs = d.attributes.min;
                //row.selectAll("td").remove();
                for(var j=0;j<attrs.length;j++){
                    row.append("td").text(attrs[j].value);
                }
            })
            /*.selectAll("body")
            .html(function(d){
                text=minAttributesToLine(d)
                return '<div style="width: '+(d.width)+'px; height: '+(d.height)+'px" class="attributes">'+text+'</div>'
            });*/
        var rowExit = row.exit();
            rowExit.remove();

    };

    function minAttributesToLine(object){
        var text = "",minattr = object.attributes.min;
        minattr.forEach(function(attr){
            text += attr.value+"  ";
        });
        return text;
    };

    function loadToolData(){
        $(document).trigger("set_loading_cursor");
        $.ajax({
            type: "GET",
            data: {system_name: JSON.stringify(scheme_names.system) },
            url: WEBVEPP.serveradr()+"webvepp/getToolData",
            error: function(xhr, ajaxOptions, thrownError) {
                $(document).trigger("unset_loading_cursor");
                $(document).trigger("error_message",thrownError);
            },
            success: function(data){
                tool_data = data["buttons"];
                setToolbar();
                $(document).trigger("tools_menu_loaded",data);
                $(document).trigger("unset_loading_cursor");
            }
        });
    };

    function setToolbar(){
        var button = tool_bar.selectAll("li.button")
            .data(tool_data);
        var buttonEnter = button.enter().insert("li")
            .attr("class", "button")
            .attr("id",function(d){
                return d.id;
            })
            .on('click', function(d){
                if(d.id!="validation"){
                    setSchemeNames(d.sample);
                    loadListSettings();
                    loadListData();
                }
                else{
                    setSchemeNames("");
                    loadValidationData();
                }
            })
            .text(function(d){
                return d.title;
            })
    };

    setSchemeNames();
    loadToolData();

    return {
    };
};