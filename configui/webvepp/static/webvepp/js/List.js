WEBVEPP.namespace("WEBVEPP.List");
WEBVEPP.List = function(){
    var list,
        scheme_names = {"system":"","sample":""},
        table = d3.select("body").select("table");

    function setSchemeNames(){
        var pathname = location.pathname;
        var path = pathname.split('/');
        if(path[1]=="webvepp"){
            scheme_names.system = "CHAN"
            if(path[2]==""){
                scheme_names.sample = "bank";
            }
            else
            {
                scheme_names.sample = path[2];
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
            .append("xhtml:body")
            .html(function(d){
                text=minAttributesToLine(d)
                return '<div style="width: '+(d.width)+'px; height: '+(d.height)+'px" class="attributes">'+text+'</div>'
            });
    };

    function minAttributesToLine(object){
        var text = "",minattr = object.attributes.min;
        minattr.forEach(function(attr){
            text += attr.value+"  ";
        });
        return text;
    }

    setSchemeNames();
    loadListData();

    return {
    };
};