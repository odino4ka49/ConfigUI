WEBVEPP.namespace("WEBVEPP.TreeModel");
WEBVEPP.TreeModel = function(){
    var tree_data = {},

        getTreeData = function(){
            var result = (tree_data===undefined)? undefined: jQuery.extend(true,{},tree_data);
            return result;
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
                    $(document).trigger("tree_changed");
                }
            });
        };

    loadTreeData();

    return {
        getTreeData: getTreeData,
    };
}