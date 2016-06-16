WEBVEPP.namespace("WEBVEPP.Scheme");
WEBVEPP.Scheme = function(menu,settings){
    var scheme_names = {},
        settings = settings;
    var scheme, schemeSVG,
        tree_scheme_names = {"system":"","sample":""},
        svg,
        scheme_button=null,
        switch_bar = d3.select("#Scheme_switcher_bar"),

        zoom = d3.behavior.zoom()
        .scale(4)
        .on('zoom', function(){
            svg.attr("transform", "translate(" + d3.event.translate + ") scale(" + d3.event.scale + ")");
        }),

        loadSchemeSample = function(){
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
                    scheme_names = data;
                    drawButtons();
                    loadScheme(getSchemeName());
                    $(document).trigger("settings_loaded",data);
                    $(document).trigger("unset_loading_cursor");
                }
            });
        },

        //zooms to defined area
        zoomToArea = function(cx,cy,areasize){
            var scale,
                canvasel = d3.select("#mainSVG")[0][0],
                canwidth = (canvasel.clientWidth || canvasel.parentNode.clientWidth)*0.8,
                canheight = (canvasel.clientHeight || canvasel.parentNode.clientHeight)*0.8,
                x = -cx,
                y = -cy,
                relation = [canwidth/areasize[0],canheight/areasize[1]];

            if(relation[0]==0) return;
            scale = (relation[0]>=relation[1])?relation[1]:relation[0];
            x += canwidth/8/scale;
            y += 50/scale;

            svg.transition()
                .duration(0)
                .attr("transform", "scale("+scale+") translate("+x+","+y+")");
            zoom.translate([x*scale,y*scale]);
            zoom.scale([scale]);
        },

        zoomToNode = function(node){
            var bbox = node.getBBox();
            var width = bbox.width,
                height = bbox.height;
            zoomToArea(bbox.x,bbox.y,[width,height]);
        },

        drawButtons = function(){
            if(scheme_names.type==null || scheme_names.type=="single")
                return;
            var buttons = switch_bar.selectAll("li")
                .data(scheme_names.schemes);
            var button = buttons.enter();
            button.append("li")
                .attr("id",function(d){
                    return "scheme_"+d.name;
                });

            var button_update = buttons;

            button_update
                .on('click', function(d){
                   //scheme_button = d.name;
                   goToScheme(d.name);
                   //reloadScheme(d.filename);
                })
                .text(function(d) {
                    if(d.name)
                        return d.name;
                });
            button_remove = buttons.exit()
                .remove();
        },

        goToScheme = function(address){
            document.location.href = WEBVEPP.serveradr() + 'webvepp/scheme/'+address;
        },

        getSchemeName = function(){
            var sname = decodeURI(location.pathname.split('/')[3]);
            if(sname == "") sname = "Main";
            $("#scheme_"+sname).addClass("active");
            if(scheme_names.type=="single"||sname==null){
                return $.grep(scheme_names.schemes, function(e){ return e.name == "Main"; })[0].filename;
            }
            else{
                return $.grep(scheme_names.schemes, function(e){ return e.name == sname; })[0].filename;
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
                var defs = xml.documentElement.getElementById("defs");
                schemeSVG = document.getElementById("schemeSVG");
                schemeSVG.appendChild(defs);
                scheme = xml.documentElement.getElementById("Слой_x0020_1");
                schemeSVG.appendChild(scheme);
                addLinks();
                svg.transition().attr("transform",'translate(' + zoom.translate() + ') scale(' + zoom.scale() + ')');
                zoomToNode(schemeSVG);
            });
        },
        addLinks = function(){
            $(".link").click(function(){
                var id = $(this).attr("link");
                var aim_system = $(this).attr("system");
                if(aim_system){
                    $(document).trigger("switch_system",aim_system);
                }
                var win = window.open(WEBVEPP.serveradr()+"webvepp/elements/"+id,'_self');
                win.onpopstate = function(){
                    alert("yeah");
                };
                //this is for new tab
                //'_blank');
                /*if(win){
                    win.focus();
                }else{
                    alert('Please allow popups for this site');
                }*/
            });
        };

    function setSchemeNames(){
        tree_scheme_names.system = settings.getSystemName();
        tree_scheme_names.sample = menu.getSampleName("scheme");
    };

    svg = d3.select("body").append("svg")
        .attr('id','mainSVG')
        .attr('width', "100%")
        .attr('height', "100%")
        .call(zoom)
        .append('g')
        .attr('id','schemeSVG');


    $(document).on("menu_loaded",function(){
        setSchemeNames();
        loadSchemeSample();
    })

    return {
    };
};
