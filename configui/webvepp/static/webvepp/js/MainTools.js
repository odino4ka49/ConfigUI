var WEBVEPP = WEBVEPP||{};
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
	return location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '')+"/";
};

$(document).on("set_loading_cursor",function(){
    document.body.style.cursor='wait';
});
$(document).on("unset_loading_cursor",function(){
    document.body.style.cursor='default';
});
$(document).ready(function(){
    var cookies = WEBVEPP.Cookies(),
        settings = WEBVEPP.Settings(cookies),
        scheme = WEBVEPP.List(d3.select("#Tool_bar"),settings),
        menu_bar = WEBVEPP.MenuBar(d3.select("#Navigation_bar"),settings);
});


