WEBVEPP.namespace("WEBVEPP.Tree");
WEBVEPP.Tree = function(params){
    var svg = params.svg,
        selector = params.selector,
        direction = params.direction,
        nodeWidth = params.nodeWidth,
        nodeHeight = params.nodeHeight,
        duration = params.duration,
        separation = params.separation,
        boxHeight = params.boxHeight,
        boxWidth = params.boxWidth,
        boxHeightMax = params.boxHeightMax,
        boxWidthMax = params.boxWidthMax,
        settings,
        tree,
        root,
        details_obj,
        additional_links,


        setChildren = function(children){
            tree.children(children);
        },
        setData = function(data){
            root = data;
        },
        setSettings = function(data){
            settings = data;
        },
        draw = function(source){
            if(root){
                var nodes = tree.nodes(root),
                    links = tree.links(nodes);
                drawNodes(nodes, source);
                drawLinks(links, source);
                drawAdditionalLinks(loadLinkEnds(root.additional_links));
                drawDetails();
            } else {
                //throw new Error('Missing root');
            }
        },
        //doesn't work
        recountXY = function(){
            var nodes = tree.nodes(root);
            nodes.forEach(function(d){
                if(d.depth==0) return;
                if("expanded" in d)
                    recountSize(d);
                //loadDetailsOpenExtra(d);
                if(d.coord) return;
                d.coord = [countNodeX(d),countNodeY(d)];
                if("collapsed" in d)
                    return
                d.collapsed = true;
            });
            checkIntersections(nodes[0]);
        },
        loadDetailsOpenExtra = function(node){
            if(node.open_extra){
                if(!node.attributes.extra || node.attributes.extra.length == 0)
                    $(document).trigger("load_details",node);
            }
        },
        recursiveYrecount = function(node){
            if(!node.children) return;
            node.children.forEach(function(child){
                child.coord[1] = countNodeY(child);
                recursiveYrecount(child);
            });
        },
        checkIntersections = function(rootnode){
            if(!rootnode.children) return;
            for(var i = 0; i<rootnode.children.length-1; i++){
                var parent1 = rootnode.children[i];
                var parent2 = rootnode.children[i+1];
                if(!parent1.children||!parent2.children) return;
                if(parent1.children.length>0 && parent2.children.length>0 && !parent1.collapsed && !parent2.collapsed){
                    var child1 = parent1.children[parent1.children.length-1];
                    var child2 = parent2.children[0];
                    var childrenlevel = settings["level"+child1.depth].display_attributes;
                    if(child1.coord[1]+childrenlevel.height/2+10>child2.coord[1]-childrenlevel.height/2){
                        parent2.coord[1]+=child1.coord[1]-child2.coord[1]+childrenlevel.height+10;
                        recursiveYrecount(parent2);
                    }
                }
            }
        },
        countNodeY = function(node){
            var index,number,
                depth = node.depth,level_name,level_info,
                pos=0;
            if(depth==0){
                return 0;
            }
            var allofus = node.parent._parents;
            var parent_y = (node.parent.coord) ? node.parent.coord[1]: 0;
            if("direction" in node && node.direction==-1){
                allofus = node.parent._children;
            }
            var index = allofus.indexOf(node);
                number = allofus.length;
                level_name = "level"+depth;
                level_info = settings[level_name].display_attributes;
            if(allofus[0].matrix) index -=1;
            if("positioning" in level_info && level_info.positioning=="matrix"){
                var matrix = $.grep(allofus, function(e){ return e.matrix; })[0];
                //var matrix = allofus[allofus.length-1]
                if(isMatrix(node)){
                    return parent_y;
                }
                else{
                    pos = Math.floor(index/matrix.cols) - Math.floor(matrix.rows/2);
                    if(matrix.rows%2==0)
                        pos+=1/2;
                }
            }
            else{
                pos = index - Math.floor(number/2);
            }
            return (10+level_info.height)*(pos)+parent_y;
        },
        countNodeX = function(node){
            var result = 0,
                depth = node.depth,
                index = 0,
                allofus,
                direction = 1,
                parent = node.parent;
            if("direction" in node && node.direction==-1){
                direction = -1;
            }
            if(node.depth!=0){
                if(direction==-1){
                    allofus = node.parent._children;
                }
                else {
                    allofus = node.parent._parents;
                }
                index = allofus.indexOf(node);
                if(allofus[0].matrix) index --;
            }
            var level_name = "level"+depth;
            var level_info = settings[level_name].display_attributes;
            //if depth == 2 and it's matrix, we just count it the way it's supposed to be
            if(depth==1){
                if ("positioning" in level_info && level_info.positioning=="matrix"){
                    var matrix = $.grep(allofus, function(e){ return e.matrix; })[0];
                    if(isMatrix(node)){
                        result+= matrix.width/2 - level_info.width - 20;
                    }
                    else{
                        result+=(index%matrix.cols)*(node.width+20) - level_info.width/2-10;
                    }
                }
                else {
                    result = 0;
                }
                return result;
            }
            else if(depth>1){
                var parent_level_name = "level"+(depth-1);
                var parent_level_info = settings[parent_level_name].display_attributes;
                if("positioning" in parent_level_info && parent_level_info.positioning=="matrix" && !("hiding" in parent_level_info && parent_level_info.hiding)){
                    var parent_level;
                    if(direction==-1){
                        parent_level= parent.parent._children;
                    }
                    else{
                        parent_level= parent.parent._parents;
                    }
                    var matrix = $.grep(parent_level, function(e){ return e.matrix; })[0];
                    //var matrix = parent_level[parent_level.length-1];
                    result = matrix.coord[0]+(matrix.width/2)*direction;
                }
                else{
                    result = parent.coord[0]+(parent.width/2)*direction;
                }
                result += 50*direction;
                if ("positioning" in level_info && level_info.positioning=="matrix"){
                    //var matrix = allofus[allofus.length-1]
                    var matrix = $.grep(allofus, function(e){ return e.matrix; })[0];
                    //result += (matrix.width/2)*direction;
                    if(isMatrix(node)){
                        result+= (matrix.width/2-10)*direction;
                    }
                    else{
                        result+=((index%matrix.cols)*(node.width+20)+node.width/2)*direction;
                    }
                }
                else{
                    result += (node.width/2)*direction;
                }
            }
            /*for(var i=1;i<=depth;i++){
                var ii = i
                if(direction==-1 && i!=1){
                        ii = -(i-1);
                }
                var level_name = ii==0? "root":"level"+ii;
                var level_info = settings[level_name].display_attributes;
                var node_width = level_info.width;
                if("positioning" in level_info && level_info.positioning=="matrix"){
                    var matrix = allofus[allofus.length-1]
                    if(i==depth){
                        if(index==allofus.length-1){
                            return countLevelX(node)-90+matrix.width/2;
                        }
                        result+=(index%matrix.cols)*(node.width+20)-45
                    }
                    else{
                        if("hiding" in level_info && level_info.hiding){
                            var unhidden,d=node;
                            while(d.depth!=i){
                                d = d.parent;
                            }
                            result = d.coord[0]+(d.width/2+20)*direction;
                        }
                        else{
                            result += matrix.width*2;
                        }
                    }
                }
                if(i!=depth)
                    result += (node_width+50)*direction;
            }*/
            return result;
        },
        countNodeClass = function(node){
            if(node.depth==0)
                return "hidden";
            var level_name = "level"+node.depth;
            var level_info = settings[level_name].display_attributes;
            var result = ""
            if("positioning" in level_info && level_info.positioning=="matrix"){
                var allofus = node.parent._parents;
                if(!node.unhidden&&!isMatrix(node)){
                    result += " inmatrix";
                }
            }
            if(node.hidden)
                result += " hidden";
            return result;
        },
        countLevelX = function(node){
            var depth = node.depth;
            if(depth==0)
                return 0;
            var result = 0,
                direction = 1;
            if("direction" in node && node.direction==-1){
                direction = -1;
            }
            for(var i=1;i<depth;i++){
                var ii = i
                if(direction==-1 && i!=1){
                        ii = -(i-1);
                }
                var level_name = ii==0? "root":"level"+ii;
                var level_info = settings[level_name].display_attributes;
                var node_width = level_info.width;
                if("positioning" in level_info && level_info.positioning=="matrix"){
                    if("hiding" in level_info && level_info.hiding){
                        var unhidden,d=node;
                        while(d.depth!=i){
                            d = d.parent;
                        }
                        result += d.coord[0]+50*direction;
                    }
                    else{
                        var columns = (level_info.matrix_size>16)? 8:4;
                        result += (node_width+30)*columns*direction;
                    }
                }
                result += (node_width+50)*direction;
            }
            return result;
        },
        isMatrix = function(person){
            /*var level_name = "level"+person.depth;
            var level_info = settings[level_name].display_attributes;
            var allofus = person.parent._parents;
            var index = allofus.indexOf(person);
            if(index==allofus.length-1 && "positioning" in level_info && level_info.positioning=="matrix"){
                return true;
            }
            return false;*/
            return person.matrix;
        },
        hideSiblings = function(person){
            var level_name = "level"+person.depth;
            var level_info = settings[level_name].display_attributes;
            var hiding = false;
            if("hiding" in level_info){
                hiding = level_info.hiding;
            }
            var nodes = tree.nodes(root);
            nodes.forEach(function(sibling){
                if(sibling.depth!=person.depth)
                    return;
                if(sibling.id!=person.id){
                    if(!("autorevealing" in level_info)||("autorevealing" in level_info && !level_info.autorevealing))
                        collapse(sibling);
                    if(hiding){
                        sibling.hidden = true;
                    }
                }
            })
            if(hiding){
                person.unhidden = true;
                if(person.open_extra){
                    person.collapsed_size = [person.width,person.height]
                    person.width = person.open_extra[0];
                    person.height = person.open_extra[1];
                }
            }
        },
        showSiblings = function(person){
            var level_name = "level"+person.depth;
            var hiding = false;
            if("hiding" in settings[level_name].display_attributes){
                hiding = settings[level_name].display_attributes.hiding;
            }
            if(hiding){
                person.unhidden = false;
                person.parent._parents.forEach(function(sibling){
                    sibling.hidden = false;
                })
                if(person.collapsed_size){
                    person.width = person.collapsed_size[0];
                    person.height = person.collapsed_size[1];
                }
            }
        },
        removeAdditionalLink = function(link){
            //root.additional_links.splice(root.additional_links.indexOf(link),1);
        },
        drawLinks = function(links, source){
            var self = this;

            var link = svg.selectAll(".link." + selector)
                .data(links, function(d){ return d.target.id; });

            var newlink = link.enter().insert("g",":first-child")
                .attr("class", "link " + selector);
            newlink.append("path")
              .attr("d", function(d) {
                var o = {x: source.x, y: direction * (source.y + boxWidth/2)};
                return transitionElbow({source: o, target: o});
              });
            newlink.append("text")
                .attr("class", "link_from");
            newlink.append("text")
                .attr("class", "link_to");

            var link_update = link.transition()
                .duration(duration);

            link_update.select("path")
                .attr("d", function(d){
                    if(d.source.depth==0)
                        return "";
                    if(d.target.direction){
                        return elbow(d, d.target.direction);
                    }
                    else{
                        return elbow(d, direction);
                    }
                });

            link_update.select("text.link_from")
                .attr("transform", function(d) {
                    if(d.source.coord)
                        return "translate(" +
                        (d.source.coord[0]/2+d.target.coord[0]/2-4) + "," +
                        (d.target.coord[1]-5) + ")";
                })
                .text(function(d) {
                    if(d.target.attributes.min){
                        for(i=0;i<d.target.attributes.min.length;i++){
                            attr = d.target.attributes.min[i];
                            if(attr.positioning=="link_text"){
                                return attr.value;
                            }
                        }
                    }
                })
                .attr("text-anchor","end")
                .attr("startOffset","100%");

            link_update.select("text.link_to")
                .attr("transform", function(d) {
                    if(d.source.coord)
                        return "translate(" +
                        (d.source.coord[0]/2+d.target.coord[0]/2+4) + "," +
                        (d.target.coord[1]-5) + ")";
                })
                .text(function(d) {
                    if(d.target.attributes.min){
                        for(i=0;i<d.target.attributes.min.length;i++){
                            attr = d.target.attributes.min[i];
                            if(attr.positioning=="link_text"&&attr.link_end_id){
                                return attr.link_end_id;
                            }
                        }
                    }
                });

            link_remove = link.exit()
                .transition()
                .duration(duration)
                .remove();

            link_remove.select("path")
              .attr("d", function(d) {
                var o = {x: source.x, y: direction * (source.y + boxWidth/2)};
                return transitionElbow({source: o, target: o});
              });

            link_remove.selectAll("text")
                .attr("transform", function(d) {
                    return "translate(" +
                        (d.source.y) + "," +
                        (d.source.x) + ")";
                });

            },
            drawNodes = function(nodes, source){

                var node = svg.selectAll("g.person." + selector)
                  .data(nodes, function(person){ return person.id; });

                // Add any new nodes
                var nodeEnter = node.enter().insert("g")
                  .attr("class", "person " + selector)
                  .attr('transform', function(person){
                    return 'translate(' + (direction * (source.y0 + person.width/2)) + ',' + source.x0 + ')';
                  })
                  .on('click', function(person){
                    togglePerson(person);
                    if("link_to_map" in person){
                        var win = window.open(WEBVEPP.serveradr()+"webvepp/"+person.link_to_map,'_self');
                    }
                  })
                  .on('wheel.zoom', function(){
                  })
                  .on('contextmenu', function(person){
                    d3.event.preventDefault();
                    if(person.type=="matrix_equation")
                        return;
                    if(!person.attributes.extra || person.attributes.extra.length == 0)
                        $(document).trigger("load_details",person);
                    revealPerson(person);
                  })

                nodeEnter.append("rect")
                  .attr({
                    x: 0,
                    y: 0,
                    rx: 10,
                    ry: 10,
                    width: 0,
                    height: 0
                  })
                  .attr("class",function(d){
                    return countNodeClass(d);
                  });

                  nodeEnter.append('foreignObject')
                        .attr('x', 0)
                        .attr('y', 0)
                        .attr('width', 0)
                        .attr('height', 0)
                        .attr("class",function(d){
                            return countNodeClass(d);
                        })
                        .append("xhtml:body");


                // Update the position of both old and new nodes
                var nodeUpdate = node;
                node.transition()
                  .duration(duration)
                  .attr("transform", function(d) { return "translate(" + (direction * d.y) + "," + d.x + ")"; });

                // Grow boxes to their proper size
                nodeUpdate.select('rect')
                  .attr('x',function(d){
                    if(d.depth==0)
                        return 0;
                    var x = d.coord[0];
                    return x-(d.width/2);
                  })
                  .attr('y',function(d){
                    if(d.depth==0)
                        return 0;
                    var y = d.coord[1];
                    return y-(d.height/2);
                  })
                  .attr('width', function(d){
                    if(d.depth==0)
                        return 0;
                    return d.width;//d.revealed ? boxWidthMax: boxWidth
                  })
                  .attr('height', function(d){
                    if(d.depth==0)
                        return 0;
                    return d.height;//d.revealed ? boxHeightMax: boxHeight
                  })
                  .attr("class",function(d){
                    return countNodeClass(d);
                  });

                // Move text to it's proper position
                nodeUpdate.select('foreignObject')
                    .attr("x", function(d){
                        if(d.depth==0)
                            return 0;
                        var x = d.coord[0];
                        return x-(d.width/2);
                    })
                    .attr("y", function(d){
                        if(d.depth==0)
                            return 0;
                        var y = d.coord[1];
                        return y-(d.height/2);
                    })
                    .attr('width', function(d){
                        if(d.depth==0)
                            return 0;
                        return d.width;//d.revealed ? boxWidthMax: boxWidth
                    })
                    .attr('height', function(d){
                        if(d.depth==0)
                            return 0;
                        return d.height;//d.revealed ? boxHeightMax: boxHeight
                    })
                    .style('fill-opacity', 1)
                      .attr("class",function(d){
                        return countNodeClass(d);
                      })
                      .select("body")
                      .html(function(d){
                            var text = "";
                            if(d.open_extra && (!d.collapsed&&("collapsed" in d))){
                                text= attributesToString(d.attributes.extra)
                            }
                            else if(d.expanded && d.attributes.extra){
                                text = attributesToString(d.attributes.extra);
                            }
                            else if(d.attributes.min){
                                text=minAttributesToString(d)
                            }
                            else if(d.type=="matrix_equation"){
                                var borders = d.noborders ? false:true;
                                text = attributesToEquation(d.attributes,borders);
                            }
                            return '<div style="width: '+(d.width)+'px; height: '+(d.height)+'px" class="attributes">'+text+'</div>'
                      });

                // Remove nodes we aren't showing anymore
                var nodeExit = node.exit()
                  .transition()
                  .duration(duration)

                  // Transition exit nodes to the source's position
                  .attr("transform", function(d) { return "translate(" + (direction * (source.y + d.width/2)) + "," + source.x + ")"; })
                  .remove();

                // Shrink boxes as we remove them
                nodeExit.select('rect')
                  .attr({
                    x: 0,
                    y: 0,
                    width: 0,
                    height: 0
                  });

                // Fade out the text as we remove it
                nodeExit.select('text')
                  .style('fill-opacity', 0)
                  .attr('x', 0);

                // Stash the old positions for transition.
                nodes.forEach(function(person) {
                    person.x0 = person.x;
                    person.y0 = person.y;
                });

                newDetailsObj();

            },
            drawAdditionalLinks = function(links){
                var self = this;

                var link = svg.selectAll(".link.additional")
                    .data(links, function(d){ return d.id; });

                var newlink = link.enter().insert("g",":first-child")
                    .attr("class", "link additional");
                newlink.append("path")
                  .attr("d", function(d) {
                    var o = {x: 0, y: 0};
                    return transitionElbow({source: o, target: o});
                  })
                  .attr("class",function(d){
                    if(d.text==null){
                        return "dashed";
                    }
                  });
                newlink.append("text");

                var link_update = link.transition()
                    .duration(duration);

                link_update.select("path")
                    .attr("d", function(d){
                        if(d.source && d.target){
                            if(d.target.direction){
                                return backward_elbow(d, d.target.direction);
                            }
                            else{
                                return backward_elbow(d, direction);
                            }
                        }
                        else{
                            removeAdditionalLink(d);
                            //link_update.remove();
                        }
                    });

                link_update.select("text")
                    .attr("transform", function(d) {
                        if(d.source && d.target)
                            return "translate(" +
                            (d.target.coord[0]+d.target.width/2+10) + "," +
                            (d.target.coord[1]-5) + ")";
                    })
                    .text(function(d) {
                        return d.text;
                    });

                link_remove = link.exit()
                    .remove();

                /*link_remove.select("path")
                  .attr("d", function(d) {
                    var o = {x: 0, y:0};
                    return transitionElbow({source: o, target: o});
                  });

                link_remove.select("text")
                    .remove();*/

            },
            drawDetails = function (){
                if(!details_obj||!details_obj.attributes.extra)
                    return;
                var details = svg.select("g.details").remove(),
                    width=0,
                    height=0;
                svg.append(function(){
                    return details.node();
                })
                if(details_obj.revealed){
                    width = boxWidthMax;
                    height = countTextHeight(details_obj.attributes.extra,width);
                }
                details.select("rect")
                    .attr('x',function(d){
                        return details_obj.coord[0]-(width/2)
                    })
                    .attr('y',function(d){
                        return details_obj.coord[1]-(height/2)-5
                    })
                    .attr('width', function(d){
                        if(width!=0)
                            return width+10;
                        else
                            return 0;
                    })
                    .attr('height', function(d){
                        return height+10;
                    });
                details.select("foreignObject")
                    .attr('x',function(d){
                        return details_obj.coord[0]-(width/2)
                    })
                    .attr('y',function(d){
                        return details_obj.coord[1]-(height/2)
                    })
                    .attr('width', function(d){
                        return width;
                    })
                    .attr('height', function(d){
                        return height;
                    })
                    .select("body")
                    .html(function(){
                        var text = attributesToString(details_obj.attributes.extra);
                        return '<div style="width: '+(width)+'px; height: '+(height)+'px" class="attributes">'+text+'</div>'
                    })
            },
            getLevelInfo = function(person){
                if(person.depth==0) return settings["root"];
                var level_name = "level"+person.depth;
                var level_info = settings[level_name].display_attributes;
                return level_info
            },
            recountSize = function(person){
                if(person.expanded){
                    person.expandwidth = boxWidthMax;
                    person.expandheight = countTextHeight(person.attributes.extra,person.width);
                    person.width = person.expandwidth;
                    person.height = person.expandheight;
                }
            },
            expandPerson = function(person){
                person.expanded = !person.expanded;
                if(person.expanded && person.expandwidth){
                    person.width = person.expandwidth;
                    person.height = person.expandheight;
                }
                else{
                    var level_info = getLevelInfo(person);
                    person.width = level_info.width;
                    person.height = level_info.height;
                }
            },
            togglePerson = function(person){
                // Don't allow the root to be collapsed because that's
                // silly (it also makes our life easier)
                if(person.depth<1 || isMatrix(person)){
                    return;
                }
                // Non-root nodes
                else {
                    var level_name = "level"+person.depth;
                    var level_info = settings[level_name].display_attributes;
                    if(level_info.autoexpanding){
                        if(!person.attributes.extra || person.attributes.extra.length == 0)
                            $(document).trigger("load_details",person);
                        expandPerson(person);
                    }
                    if(level_info.autorevealing){
                        return;
                    }
                    if(person.collapsed){
                        if(person._parents.length==0)
                            $(document).trigger("load_neighbours",person);
                        person.collapsed = false;
                        if(person.open_extra&&person.attributes.extra.length==0){
                            loadDetailsOpenExtra(person);
                        }
                        //if we don't want to see any sibling's _parents
                        hideSiblings(person);
                    } else {
                        showSiblings(person);
                        collapse(person);
                    }
                    draw(person);
                }
            },
            revealPerson = function(person){
                person.revealed = !person.revealed;
                details_obj = person;
                drawDetails();
            },
            hideDetails = function(person){
                if(person){
                    person.revealed = false;
                    drawDetails();
                }
            };

    tree = d3.layout.tree()
        //.nodeSize([nodeWidth, nodeHeight])
        .separation(function(a, b) {
               var height = (a.height + b.height)/100,
                   distance = height / 2 + 0.1; // horizontal distance between nodes = 16
                   return distance;
           });
    function newDetailsObj(){
        if(!svg.select("g.details").empty())
            return;
        var det_obj = svg.append("g").attr("class", "details")
            .on("contextmenu",function(){
                d3.event.preventDefault();
                revealPerson(details_obj);
            })
            .on("mouseout",function(){
                hideDetails(details_obj);
            });
        det_obj.append("rect")
            .attr({
                x: 0,
                y: 0,
                rx: 10,
                ry: 10,
                width: 0,
                height: 0
            });
        det_obj.append('foreignObject')
            .attr('x', 0)
            .attr('y', 0)
            .attr('width', 0)
            .attr('height', 0)
            .append("xhtml:body")
            /*.html(function(d){
                var text = attributesToString(d.attributes.min);
                text += d.revealed? attributesToString(d.attributes.extra): "";
                return '<div style="width: '+(boxWidth)+'px; height: '+(boxHeight)+'px" class="attributes">'+text+'</div>'
            })*/;
    };
    function findObjectById(id){
        var nodes = tree.nodes(root);
        var node = nodes.filter(function(n){
            return n.id==id;
        });
        return node[0];
    };
    function findObjectByName(name){
        var nodes = tree.nodes(root);
        var node = nodes.filter(function(n){
            return n.name==name;
        });
        return node[0];
    };
    function collapse(person){
        person.collapsed = true;
        /*if(person._parents){
            person._parents.forEach(collapse);
        }
        if(person._children){
            person._children.forEach(collapse);
        }*/
    };
    function uncollapse(person){
        person.collapsed = false;
            if(person._parents){
                person._parents.forEach(uncollapse);
            }
            if(person._children){
                person._children.forEach(uncollapse);
        }
    };
    function loadLinkEnds(links){
        if(!links) return;
        for(i=0;i<links.length;i++){
            var link = links[i];
            link.target = findObjectById(link.to);
            link.source = findObjectById(link.from);
        }
        return links;
    };
    function elbow(d, direction) {
        /*var sourceX = d.source.x,
          sourceY = d.source.y + (boxWidth / 2),
          targetX = d.target.x,
          targetY = d.target.y - (boxWidth / 2);*/
        var sourceX = d.source.coord[1],
        sourceY = d.source.coord[0] + (d.source.width / 2)*direction,
        targetX = d.target.coord[1],
        targetY = d.target.coord[0] - (d.target.width / 2)*direction,
        target_levelY = countLevelX(d.target) - (d.target.width / 2)*direction;

        if(d.source.depth!=0){
            var level_info = settings["level"+d.target.depth].display_attributes;
            if("positioning" in level_info && level_info.positioning=="matrix"){
                return "M" + (direction * sourceY) + "," + sourceX + "H" + (direction * targetY);
            }
        }

        return "M" + (sourceY) + "," + sourceX
        + "H" + ((sourceY + (target_levelY-sourceY)/2))
        + "V" + targetX
        + "H" + (targetY);
    };
    function backward_elbow(d,direction) {
        var sourceX = d.source.coord[1],
        sourceY = d.source.coord[0] - (d.source.width / 2),
        targetX = d.target.coord[1],
        targetY = d.target.coord[0] + (d.target.width / 2),
        target_levelY = countLevelX(d.target) + (d.target.width / 2);

        if(sourceY==target_levelY - d.target.width ){
            target_levelY = target_levelY+50;
            sourceY = targetY;
        }

        return "M" + (direction * sourceY) + "," + sourceX
        + "H" + (direction * (sourceY + (target_levelY-sourceY)/2))
        + "V" + targetX
        + "H" + (direction * targetY);
    };
    function transitionElbow(d){
        return "M" + d.source.y + "," + d.source.x
            + "H" + d.source.y
            + "V" + d.source.x
            + "H" + d.source.y;
    };
    function countTextHeight(rows,width){
        var rows_number = 0,row;
        for(i=0;i<rows.length;i++){
            var row_width;
            row = rows[i];
            if(row.value==null){
                row_width += row.key.length*6;
            }
            else{
                row_width = (row.key.length+row.value.length+2)*10;
            }
            rows_number+=(row_width/width>>0)+1;
        }
        return rows_number*17+20;
    };
    function minAttributesToString(d){
        var level_info = getLevelInfo(d);
        if(level_info.field_name){
            return attributesToString(d.attributes.min);
        }
        else{
            return attributesToShortString(d.attributes.min,level_info.inline)
        }
    };
    function attributesToString(attributes){
        var text = "";
        attributes.forEach(function(attr){
            if(!attr.positioning)
                text += attr.key+": "+attr.value+"<br/>";
        });
        return text;
    };
    function attributesToShortString(attributes,inline){
        var text = "";
        attributes.forEach(function(attr){
            if(attr.key=="Index" || inline){
                text += "<div style='display: inline-table;'>" + attr.value+"</div><div style='display: inline-table; margin-left:5px'>";
            }
            else{
                text += attr.value+"<br/>";
            }
        });
        text += "</div>";
        return text;
    };
    function attributesToEquation(attributes,borders){
        var text = "";
        text += "<table><tr><td>";
        if(attributes[1]!=null){
            text += borders ? matrixToTable(attributes[0]):attributes[0][0];
            text += "</td><td>=</td><td>";
            text += borders ? matrixToTable(attributes[1]):attributes[1][0];
            text += "</td><td>x</td><td>";
            text += borders ? matrixToTable(attributes[2]):attributes[2][0];
            text += "</td></tr></table><table><tr><td>";
        }
        if(attributes[4]!=null){
            text += borders ? matrixToTable(attributes[3]):attributes[3][0];
            text += "</td><td>=</td><td>";
            text += borders ? matrixToTableReversed(attributes[4]):attributes[4][0];
            text += "</td><td>x</td><td>";
            text += borders ? matrixToTable(attributes[5]):attributes[5][0];
            text += "</td></tr></table><table><tr><td>";
        }
        if(attributes[7]){
            text += borders ? matrixToTable(attributes[6]):attributes[6][0];
            text += "</td><td>=</td><td>";
            text += borders ? matrixToTable(attributes[7]):attributes[7][0];
        }
        text += "</td></tr></table>";
        return text;
    };
    function matrixToTable(matrix){
        if(matrix==null){
            return "<table><tr><td>Null</td></tr></table>";
        }
        var matrixtype = (!Array.isArray(matrix[0])) ? "vector":"matrix";
        var table = "<table class='matrix'>";
        matrix.forEach(function(row){
            table += "<tr>"
            if(matrixtype == "vector"){
                table += "<td>"+row+"</td>";
            }
            else{
                row.forEach(function(item){
                    table += "<td>"+item+"</td>";
                })
            }
            table+="</tr>"
        });
        table += "</table>";
        return table;
    };
    function matrixToTableReversed(matrix){
        if(matrix==null){
            return "<table><tr><td>Null</td></tr></table>";
        }
        var matrixtype = (!Array.isArray(matrix[0])) ? "vector":"matrix";
        var table = "<table class='matrix'>";
        var rows_number = matrix[0].length;
        var columns_number = matrix.length;
        if(matrixtype=="vector"){
            rows_number = matrix.length;
            columns_number = 0;
        }
        for(i=0;i<rows_number;i++){
            table+="<tr>";
            if(matrixtype!="vector"){
                for(j=0;j<columns_number;j++){
                    table += "<td>"+matrix[j][i]+"</td>";
                }
            }
            else{
                table += "<td>"+matrix[i]+"</td>";
            }
            table += "</tr>";
        }
        table += "</table>";
        return table;
    };
    function movePerson(person,shift){
        if(person.coord){
            person.coord = [person.coord[0]+shift[0],person.coord[1]+shift[1]];
        }
    };
    function moveToStartPosition(person){
        var coords = person.coord;
        var nodes = tree.nodes(root);
        var shift = [-coords[0],-coords[1]];
        nodes.forEach(function(n){
            movePerson(n,shift);
        });
    };

    return {
        setChildren:setChildren,
        setData:setData,
        setSettings: setSettings,
        draw:draw,
        drawNodes:drawNodes,
        drawLinks:drawLinks,
        togglePerson:togglePerson,
        recountXY:recountXY,
        findObjectByName: findObjectByName,
        moveToStartPosition: moveToStartPosition,
    };
};