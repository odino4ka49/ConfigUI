WEBVEPP.namespace("WEBVEPP.Scheme");
WEBVEPP.Scheme = function(settings){
    var scheme_names = {"system":"","sample":""},
        settings = settings;
    var scheme, schemeSVG,
        svg,

        zoom = d3.behavior.zoom()
        .scale(4)
        .on('zoom', function(){
            svg.attr("transform", "translate(" + d3.event.translate + ") scale(" + d3.event.scale + ")");
        }),

        getSchemeName = function(){
            var system_name = settings.getSystemName();
            switch(system_name){
                case "CHAN":
                    return "Chan_V3-V4_scheme_bbg"
                case "V4":
                    return null
                default:
                    return null
                }
        },

        loadScheme = function(scheme_name){
            var parser = new DOMParser();
            if(!scheme_name)
                return;
            d3.xml(WEBVEPP.serveradr()+"static/webvepp/bg/"+scheme_name+".svg", "image/svg+xml", function(error, xml) {
                if (error) throw error;
                var defs = xml.documentElement.getElementById("defs");
                document.getElementById("schemeSVG").appendChild(defs);
                scheme = xml.documentElement.getElementById("Слой_x0020_1");
                document.getElementById("schemeSVG").appendChild(scheme);
                addLinks();
                svg.transition().attr("transform",'translate(' + zoom.translate() + ') scale(' + zoom.scale() + ')');
            });
        },
        addLinks = function(){
            $(".link").click(function(){
                var id = $(this).attr("link");
                var win = window.open(WEBVEPP.serveradr()+"webvepp/elements/"+id,'_self');
                //this is for new tab
                //'_blank');
                /*if(win){
                    win.focus();
                }else{
                    alert('Please allow popups for this site');
                }*/
            });
        };

    svg = d3.select("body").append("svg")
        .attr('width', "100%")
        .attr('height', "100%")
        .call(zoom)
        .append('g')
        .attr('id','schemeSVG');
    loadScheme(getSchemeName());

    return {
    };
};
