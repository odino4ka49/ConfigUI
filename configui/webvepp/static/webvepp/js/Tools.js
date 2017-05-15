WEBVEPP.namespace("WEBVEPP.List");
WEBVEPP.List = function(tool_bar,settings){
    var list, list_settings,
        settings = settings,
        tool_data = [],
        image_data = "",
        scheme_names = {"system":"","sample":""},
        table = d3.select("body").select("table"),
        legend = d3.select("body").select("#legend"),
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
                drawLegend();
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
        legend.text("");
        table.select('thead').remove();
        table.select('tbody').remove();
        var thead = table.append('thead');
        var tbody = table.append('tbody');
        tbody.append("tr").append("td").text(text_data);
    };

    function drawImageData(filename,width){
        legend.text("");
        table.select('thead').remove();
        table.select('tbody').remove();
        var thead = table.append('thead');
        var tbody = table.append('tbody');
        thead.append("tr").append("td").append("img")
            .attr("src",WEBVEPP.serveradr()+"static/webvepp/bg/"+filename)
            .attr("alt","Image tool")
            .attr("width",width);
    };

    function drawLegend(){
        if(list_settings.legend){
            legend.text(list_settings.legend);
        }
        else{
            legend.text("");
        }
    };

    function drawListData(){
        table.select('thead').remove();
        table.select('tbody').remove();
        var thead = table.append('thead');
        var tbody = table.append('tbody');
        var list_attrs = list_settings.root.display_filter.min;
        var list_titles = [];
        thead.append("tr")
            .each(function(d,i){
                var row = d3.select(this);
                if(!list_settings) return;
                //var attrs = list_settings.root.display_filter.min;
                if(list_settings.root.display_attributes.sort_type=="numbered"){
                    list_attrs.unshift("Index");
                    //row.append("td").text("Index")
                }
                for(var j=0;j<list_attrs.length;j++){
                    var key = "";
                    if(typeof(list_attrs[j])=="string"){
                        key = list_attrs[j];
                    }
                    else if(typeof(list_attrs[j]=="object")){
                        key = list_attrs[j].key;
                    }
                    row.append("td").text(key);
                    list_titles.push(key);
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
                for(var j=0;j<list_attrs.length;j++){
                    var attr_name = list_titles[j];
                    var attr_field = attrs.filter(function( obj ) { return obj.key == attr_name; })[0];
                    var attr_value="";
                    if(attr_field){
                        attr_value = attr_field.value;
                    }
                    if(list_attrs[j].type=="image"){
                        row.append("td").append("img")
                            .attr("src",WEBVEPP.serveradr()+"static/webvepp/bg/"+attr_value)
                            .attr("alt",attrs[j].value)
                            .attr("width",list_attrs[j].width);
                    }
                    else if(attr_value instanceof Array){
                        var rowvalue = row.append("td");
                        for(var i in attr_value){
                            rowvalue.append("div").text(attr_value[i]);
                        }
                    }
                    else{
                        row.append("td").text(attr_value);
                    }
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
                if(d.type=="list"){
                    setSchemeNames(d.sample);
                    loadListSettings();
                    loadListData();
                }
                else if(d.type=="validation"){
                    setSchemeNames("");
                    loadValidationData();
                }
                else if(d.type=="image"){
                    var width = "60%";
                    setSchemeNames(d.sample);
                    if(d.width) width = d.width;
                    drawImageData(d.filename,width);
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