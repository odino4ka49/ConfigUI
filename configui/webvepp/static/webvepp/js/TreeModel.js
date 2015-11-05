WEBVEPP.namespace("WEBVEPP.TreeModel");
WEBVEPP.TreeModel = function(){
    var tree_data = {},

        getTreeData = function(){
            var result = tree_data;//(tree_data===undefined)? undefined: jQuery.extend(true,{},tree_data);
            return result;
        },

        addNodeNeighbours= function(node,neighbours){
            //var tree_node = tree_data.filter(function(d){return (d.id === node.id);})[0];
            //tree_node._parents = neighbours;
        };

    function loadTreeData(){
            $(document).trigger("set_loading_cursor");
            $.ajax({
                type: "GET",
                url: WEBVEPP.serveradr()+"webvepp/getTreeData",
                error: function(xhr, ajaxOptions, thrownError) {
                    $(document).trigger("unset_loading_cursor");
                    $(document).trigger("error_message",thrownError);
                },
                success: function(data){
                    tree_data = data;
                    console.log(tree_data);
                    $(document).trigger("unset_loading_cursor");
                    $(document).trigger("tree_created");
                }
            });
        };

    function loadNodeNeighbours(node){
            $(document).trigger("set_loading_cursor");
            $.ajax({
                type: "GET",
                url: WEBVEPP.serveradr()+"webvepp/getNodeNeighbours",
                data: {node_id:node.id,level:node.depth},
                error: function(xhr, ajaxOptions, thrownError) {
                    $(document).trigger("unset_loading_cursor");
                    $(document).trigger("error_message",thrownError);
                },
                success: function(data){
                    node._parents = data;
                    $(document).trigger("unset_loading_cursor");
                    $(document).trigger("tree_changed");
                }
            });
        };

    loadTreeData();

    return {
        getTreeData: getTreeData,
        loadNodeNeighbours: loadNodeNeighbours,
    };
}