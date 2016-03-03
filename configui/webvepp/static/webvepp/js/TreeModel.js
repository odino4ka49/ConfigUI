WEBVEPP.namespace("WEBVEPP.TreeModel");
WEBVEPP.TreeModel = function(settings){
    var tree_data = {},
        tree_settings = {},
        tree_scheme_names = {"system":"","sample":""},
        settings = settings,

        getTreeData = function(){
            var result = tree_data;//(tree_data===undefined)? undefined: jQuery.extend(true,{},tree_data);
            return result;
        },

        getTreeSettings = function(){
            return tree_settings;
        };

    function setSchemeNames(){
        var pathname = location.pathname;
        var path = pathname.split('/');
        tree_scheme_names.system = settings.getSystemName();
        if(path[1]=="webvepp"){
            if(path[2]==""||path[2]=="camacs"){
                tree_scheme_names.sample = "camacs";
            }
            else
            {
                tree_scheme_names.sample = path[2];
            }
        }
    };

    function loadTreeData(filter_name){
            if(!filter_name)
                filter_name = null
            $(document).trigger("set_loading_cursor");
            $.ajax({
                type: "GET",
                data: {scheme_names: JSON.stringify(tree_scheme_names),filter_name: JSON.stringify(filter_name) },
                url: WEBVEPP.serveradr()+"webvepp/getTreeData",
                error: function(xhr, ajaxOptions, thrownError) {
                    $(document).trigger("unset_loading_cursor");
                    $(document).trigger("error_message",thrownError);
                },
                success: function(data){
                    tree_data = data;
                    $(document).trigger("unset_loading_cursor");
                    $(document).trigger("tree_created");
                }
            });
        };

    function loadTreeSettings(){
            $(document).trigger("set_loading_cursor");
            $.ajax({
                type: "GET",
                data: {scheme_names: JSON.stringify(tree_scheme_names) },
                url: WEBVEPP.serveradr()+"webvepp/getTreeSample",
                error: function(xhr, ajaxOptions, thrownError) {
                    $(document).trigger("unset_loading_cursor");
                    $(document).trigger("error_message",thrownError);
                },
                success: function(data){
                    tree_settings = data;
                    $(document).trigger("settings_loaded",data);
                    $(document).trigger("unset_loading_cursor");
                }
            });
        };

    function loadNodeNeighbours(node){
            $(document).trigger("set_loading_cursor");
            $.ajax({
                type: "GET",
                url: WEBVEPP.serveradr()+"webvepp/getNodeNeighbours",
                data: {node_id:node.id,level:node.depth,scheme_names: JSON.stringify(tree_scheme_names) },
                error: function(xhr, ajaxOptions, thrownError) {
                    $(document).trigger("unset_loading_cursor");
                    $(document).trigger("error_message",thrownError);
                },
                success: function(data){
                    node._parents = data[0];
                    console.log(data[0]);
                    node._children = data[1];
                    if(data[3]){
                        node._parents.push(data[3]);
                    }
                    tree_data.additional_links = unique_check(tree_data.additional_links.concat(data[2]));
                    $(document).trigger("unset_loading_cursor");
                    $(document).trigger("tree_changed");
                }
            });
        };
    function loadDetails(node){
        $(document).trigger("set_loading_cursor");
            $.ajax({
                type: "GET",
                url: WEBVEPP.serveradr()+"webvepp/getMaxAttributes",
                data: {node_id:node.id,level:node.depth,scheme_names: JSON.stringify(tree_scheme_names) },
                error: function(xhr, ajaxOptions, thrownError) {
                    $(document).trigger("unset_loading_cursor");
                    $(document).trigger("error_message",thrownError);
                },
                success: function(data){
                    node.attributes.extra = data;
                    $(document).trigger("unset_loading_cursor");
                    $(document).trigger("tree_changed");
                }
            });
    };

    function unique_check(array){
        var a = array;
        for(var i=0; i<a.length; ++i) {
            for(var j=i+1; j<a.length; ++j) {
                if(a[i].id === a[j].id)
                    a.splice(j--, 1);
            }
        }
        return a;
    }

    setSchemeNames();
    loadTreeSettings();
    loadTreeData();


    $(document).on("reload_tree",function(event,filter_name){
        loadTreeData(filter_name);
    });

    return {
        getTreeData: getTreeData,
        getTreeSettings: getTreeSettings,
        loadNodeNeighbours: loadNodeNeighbours,
        loadDetails: loadDetails,
    };
}