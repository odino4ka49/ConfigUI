WEBVEPP.namespace("WEBVEPP.TreeController");
WEBVEPP.TreeController = function(model,view){
    var tree_view = view,
        tree_model = model
        ;

    $(document).on("load_neighbours",function(event,d){
        tree_model.loadNodeNeighbours(d);
    });
    $(document).on("load_details",function(event,d){
        tree_model.loadDetails(d);
    });

    return{

    };
};