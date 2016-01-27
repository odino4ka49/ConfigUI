WEBVEPP.namespace("WEBVEPP.Scheme");
WEBVEPP.Scheme = function(){
    var scheme = scheme,
        svg,

        zoom = d3.behavior.zoom()
        .scale(4)
        .on('zoom', function(){
            svg.attr("transform", "translate(" + d3.event.translate + ") scale(" + d3.event.scale + ")");
        }),

        loadScheme = function(){
            /*$(document).trigger("set_loading_cursor");
            $.ajax({
                type: "GET",
                data: {scheme_name: JSON.stringify("Chan_V3-V4_scheme-no_lines_black") },
                url: WEBVEPP.serveradr()+"webvepp/getSchemeData",
                //accepts: "application/xml",
                error: function(xhr, ajaxOptions, thrownError) {
                    $(document).trigger("unset_loading_cursor");
                    console.log(xhr);
                    $(document).trigger("error_message",thrownError);
                },
                success: function(data){
                    scheme = data;
                    console.log("hi");
                    $(document).trigger("unset_loading_cursor");
                }
            });*/
            var parser = new DOMParser();
            d3.xml(WEBVEPP.serveradr()+"static/webvepp/bg/"+"Chan_V3-V4_scheme-no_lines_black.svg", "image/svg+xml", function(error, xml) {
                if (error) throw error;
                //console.log(xml.documentElement.getElementById("Слой_x0020_1"));
                var defs = xml.documentElement.getElementById("defs");
                document.getElementById("schemeSVG").appendChild(defs)
                scheme = xml.documentElement.getElementById("Слой_x0020_1");
                var schemeSVG = document.adoptNode(scheme)
                document.getElementById("schemeSVG").appendChild(scheme)
                //svg.append(scheme);
                //document.body.appendChild(group);
            });
                //.call(zoom);
        };

    svg = d3.select("body").append("svg")
        .attr('width', "100%")
        .attr('height', "100%")
        .call(zoom)
        .append('g')
        .attr('id','schemeSVG');
    loadScheme();

    return {
    };
};
