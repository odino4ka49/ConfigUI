WEBVEPP.namespace("WEBVEPP.List");
WEBVEPP.List = function(tool_bar,settings){
    var list, list_settings,
        settings = settings,
        tool_data = [],
        image_data = "",
        scheme_names = {"system":"","sample":""},
        table = d3.select("body").select("table"),
        legend = d3.select("body").select("#legend"),
        toolbar = d3.select("body").select("#toolbar"),
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

        resetTableExport();

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

        resetTableExport();
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
        var tbody = table.append('tbody').attr("class","list");
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
                    row.append("td")
                    .append("button")
                    .attr("class","sort")
                    .attr("data-sort",key)
                    .text(key);
                    list_titles.push(key);
                }
            })

        var row = tbody.selectAll("tr").data(list);
        var rowEnter = row.enter().append("tr")

        var rowUpdate = row;
            rowUpdate.each(function(d,i){
                var row = d3.select(this);
                var attrs = d.attributes.min;
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
                        var rowvalue = row.append("td").attr("class",attr_name);
                        for(var i in attr_value){
                            rowvalue.append("div").append("text").text(attr_value[i]);
                        }
                    }
                    else{
                        row.append("td").text(attr_value).attr("class",attr_name);
                    }
                }
            })
        var rowExit = row.exit();
            rowExit.remove();

        resetTableExport();
    };

    function minAttributesToLine(object){
        var text = "",minattr = object.attributes.min;
        minattr.forEach(function(attr){
            text += attr.value+"  ";
        });
        return text;
    };

    function setSearch(){
        $("#search").removeClass("hidden");
        var list_attrs = list_settings.root.display_filter.min;
        var options = {valueNames: []};
        for(var j=0;j<list_attrs.length;j++){
            var key = "";
            if(typeof(list_attrs[j])=="string"){
                key = list_attrs[j];
            }
            else if(typeof(list_attrs[j]=="object")){
                key = list_attrs[j].key;
            }
            options["valueNames"].push(key);
        };
        var searchList = new List('search_list',options);
    };

    function unsetSearch(){
        $("#search").addClass("hidden");
        $(document).off("tree_created");
    };

    function activate(id){
        toolbar.selectAll("li").classed("active",false);
        $("#"+id).addClass("active");
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
                unsetSearch();
                activate(d.id);
                if(d.type=="list"){
                    setSchemeNames(d.sample);
                    loadListSettings();
                    loadListData();
                    $(document).on("tree_created",function(event,d){
                        setSearch();
                    });
                }
                else if(d.type=="search"){
                    setSchemeNames(d.sample);
                    loadListSettings();
                    loadListData();
                    $(document).on("tree_created",function(event,d){
                        setSearch();
                    });
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

    function resetTableExport(){
        jtable.reset();
    }

    function setTableExport(){
        TableExport.prototype.txt = {
            defaultClass: "txt",
            buttonContent: "Export to txt",
            separator: "\t|",
            mimeType: "text/plain",
            fileExtension: ".txt"
        };

        jtable = TableExport(document.getElementById("list"),{
            bootstrap: false,
            formats: ["txt"],
            position: "bottom"
        })
/*
        $exportbutton = $("#list").find('caption').children().detach();
        $exportbutton.appendTo('#search');*/
    };

    setSchemeNames();
    loadToolData();
    setTableExport();

    return {
    };
};