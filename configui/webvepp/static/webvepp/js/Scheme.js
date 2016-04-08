WEBVEPP.namespace("WEBVEPP.Scheme");
WEBVEPP.Scheme = function(settings){
    var scheme_names = {},
        settings = settings;
    var scheme, schemeSVG,
        svg,
        scheme_button=null,
        switch_bar = d3.select("#Scheme_switcher_bar"),

        zoom = d3.behavior.zoom()
        .scale(4)
        .on('zoom', function(){
            svg.attr("transform", "translate(" + d3.event.translate + ") scale(" + d3.event.scale + ")");
        }),

        //заглушка
        setSchemeSample = function(){
            var system_name = settings.getSystemName();
            switch(system_name){
                case "CHAN":
                    scheme_names = {
                        "name": "Scheme",
                        "type": "single",
                        "schemes": [
                          {
                            "name": "Main",
                            "filename": "Chan_V3-V4_scheme_bbg"
                          }
                        ]
                      }
                    break;
                case "V4":
                    scheme_names = {
                        "name": "Scheme",
                        "type": "list",
                        "schemes": [
                            {
                              "name":"Main",
                              "filename": "vepp4_main"
                            },
                            {
                              "name":"Non-linear",
                              "filename": "vepp4_RF_elstat_non-linear",
                            },
                            {
                              "name":"Orbit",
                              "filename": "vepp4_corr_X_Z",
                            },
                            {
                              "name":"Gradient",
                              "filename": "vepp4_gradient"
                            }
                        ]
                    }
                    break;
                default:
                    scheme_names = {"type":null,"schemes":{}}
                    break;
               }
        },

        drawButtons = function(){
            if(scheme_names.type==null || scheme_names.type=="single")
                return;
            var buttons = switch_bar.selectAll("li")
                .data(scheme_names.schemes);
            var button = buttons.enter();
            button.append("li");

            var button_update = buttons;

            button_update
                .on('click', function(d){
                   scheme_button = d.name;
                   reloadScheme(d.filename);
                })
                .text(function(d) {
                    if(d.name)
                        return d.name;
                });
            button_remove = buttons.exit()
                .remove();
        },

        getSchemeName = function(){
            if(scheme_names.type=="single"||scheme_button==null){
                return $.grep(scheme_names.schemes, function(e){ return e.name == "Main"; })[0].filename;
            }
            else{
                return $.grep(scheme_names.schemes, function(e){ return e.name == "scheme_button"; }).filename;
            }
        },

        reloadScheme = function(scheme_name){
            myNode = document.getElementById("schemeSVG");
            while (myNode.firstChild) {
                myNode.removeChild(myNode.firstChild);
            }
            loadScheme(scheme_name);
        },

        loadScheme = function(scheme_name){
            var parser = new DOMParser();
            if(!scheme_name)
                return;
            d3.xml(WEBVEPP.serveradr()+"static/webvepp/bg/"+scheme_name+".svg", "image/svg+xml", function(error, xml) {
                if (error) throw error;
                console.log(xml);
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
    setSchemeSample();
    drawButtons();
    loadScheme(getSchemeName());

    return {
    };
};
