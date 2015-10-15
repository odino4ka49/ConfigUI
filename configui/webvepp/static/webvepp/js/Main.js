var WEBVEPP = WEBVEPP||{};
//создание пространства имен
WEBVEPP.namespace = function (ns_string) {
    var parts = ns_string.split('.'),
        parent = WEBVEPP,
        i;
    if (parts[0] === "WEBVEPP") {
        parts = parts.slice(1);
    }
    for (i = 0; i < parts.length; i += 1) {
        if (typeof parent[parts[i]] === "undefined") {
            parent[parts[i]] = {};
        }
        parent = parent[parts[i]];
    }
    return parent;
};
WEBVEPP.serveradr = function(){
	return "http://127.0.0.1:8000/";
};
$(document).ready(function(){
    var tree_model = WEBVEPP.TreeModel(),
        tree = "",
        tree_view = WEBVEPP.TreeView(tree_model,{
            //"canvas": d3.select("#tree_map"),
            "body": d3.select("body")
        },tree);
        /*tree_controller = WEBVEPP.TreeController({
            "storage": storage
        },tree_view);*/
});