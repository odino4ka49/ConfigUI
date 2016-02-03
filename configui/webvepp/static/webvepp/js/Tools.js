WEBVEPP.namespace("WEBVEPP.List");
WEBVEPP.List = function(){
    var list,
        scheme_names = {"system":"","sample":""},
        table = d3.select("body").select("table");

    function setSchemeNames(tool_name){
        var pathname = location.pathname;
        var path = pathname.split('/');
        if(path[1]=="webvepp"){
            scheme_names.system = "CHAN"
            if(path[2]=="tools"){
                if(tool_name=="bank"){
                    scheme_names.sample = "bank";
                }
                else if(tool_name=="tool_modules"){
                    scheme_names.sample = "tool_modules";
                }
                else
                {
                    scheme_names.sample = "";
                }
            }
            else
            {
                scheme_names.sample = "";
            }
        }
    };

    function loadListData(){
        $(document).trigger("set_loading_cursor");
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
                console.log(data);
                drawListData();
                $(document).trigger("unset_loading_cursor");
                $(document).trigger("tree_created");
            }
        });
    };

    function drawListData(){
        var row = table.selectAll("tr").data(list)
        var rowEnter = row.enter().append("tr").append("td")
            .append('foreignObject')
            .append("xhtml:body");
        var rowUpdate = row;
            rowUpdate.selectAll("body")
            .html(function(d){
                text=minAttributesToLine(d)
                return '<div style="width: '+(d.width)+'px; height: '+(d.height)+'px" class="attributes">'+text+'</div>'
            });
        var rowExit = row.exit();
            rowExit.remove();

    };

    function minAttributesToLine(object){
        var text = "",minattr = object.attributes.min;
        minattr.forEach(function(attr){
            text += attr.value+"  ";
        });
        return text;
    }

    function setToolbar(){
        $("#tool_bank").click(function(){
            setSchemeNames("bank");
            loadListData();
        })
        $("#tool_modules").click(function(){
            setSchemeNames("tool_modules");
            loadListData();
        })
    }

    setToolbar();

    return {
    };
};