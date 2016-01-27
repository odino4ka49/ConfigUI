WEBVEPP.namespace("WEBVEPP.Scheme");
WEBVEPP.Scheme = function(){
    var scheme = scheme,
        svg,

        loadScheme = function(){
            $(document).trigger("set_loading_cursor");
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
            });
            /*d3.xml("", "image/svg+xml", function(error, xml) {
                if (error) throw error;
                document.body.appendChild(xml.documentElement);
            });*/
            svg = d3.select("body").select("svg")
                .attr('width', "100%")
                .attr('height', "100%");
                //.call(zoom);
        };

    loadScheme();

    return {
    };
};
