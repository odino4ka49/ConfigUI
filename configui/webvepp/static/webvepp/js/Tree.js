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
                loadDetailsOpenExtra(d);
                if(d.coord) return;
                d.coord = [countNodeX(d),countNodeY(d)];
            });
        },
        loadDetailsOpenExtra = function(node){
            if(node.open_extra){
                if(!node.attributes.extra || node.attributes.extra.length == 0)
                    $(document).trigger("load_details",node);
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
            if("positioning" in level_info && level_info.positioning=="matrix"){
                var matrix = allofus[allofus.length-1]
                if(index==number-1){
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
            }
            var level_name = "level"+depth;
            var level_info = settings[level_name].display_attributes;
            //if depth == 2 and it's matrix, we just count it the way it's supposed to be
            if(depth==1){
                if ("positioning" in level_info && level_info.positioning=="matrix"){
                    var matrix = allofus[allofus.length-1]
                    if(index==allofus.length-1){
                        result+= matrix.width/2 - level_info.width - 20;
                    }
                    else{
                        result+=(index%matrix.cols)*(node.width+20) - level_info.width/2-10;
                    }
                }
                else{
                    result = 0;
                }
                return result;
            }
            else if(depth>1){
                var parent_level_name = "level"+(depth-1);
                var parent_level_info = settings[level_name].display_attributes;
                if("positioning" in parent_level_info && parent_level_info.positioning=="matrix" && !("hiding" in parent_level_info && parent_level_info.hiding)){
                    var parent_level;
                    if(direction==-1){
                        parent_level= parent.parent._children;
                    }
                    else{
                        parent_level= parent.parent._parents;
                    }
                    var matrix = parent_level[parent_level.length-1];
                    result = matrix.coord[0]+(matrix.width/2)*direction;
                }
                else{
                    result = parent.coord[0]+(parent.width/2)*direction;
                }
                result += 50*direction;
                if ("positioning" in level_info && level_info.positioning=="matrix"){
                    var matrix = allofus[allofus.length-1]
                    //result += (matrix.width/2)*direction;
                    if(index==allofus.length-1){
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
                if(!node.unhidden&&allofus.indexOf(node)!=allofus.length-1){
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
            var level_name = "level"+person.depth;
            var level_info = settings[level_name].display_attributes;
            var allofus = person.parent._parents;
            var index = allofus.indexOf(person);
            if(index==allofus.length-1 && "positioning" in level_info && level_info.positioning=="matrix"){
                return true;
            }
            return false;
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
                if(person.open_extra){
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
            newlink.append("text");

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

            link_update.select("text")
                .attr("transform", function(d) {
                    return "translate(" +
                        (d.target.y-boxWidth/2-20) + "," +
                        (d.target.x-5) + ")";
                })
                .text(function(d) {
                    if(d.target.link_id)
                     return d.target.link_id;
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

            link_remove.select("text")
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
                var nodeEnter = node.enter().insert("g",":first-child")
                  .attr("class", "person " + selector)

                  // Add new nodes at the right side of their child's box.
                  // They will be transitioned into their proper position.
                  .attr('transform', function(person){
                    return 'translate(' + (direction * (source.y0 + person.width/2)) + ',' + source.x0 + ')';
                  })
                  .on('click', function(person){
                    togglePerson(person);
                    if("link_to_map" in person){
                        var win = window.open(WEBVEPP.serveradr()+"webvepp/"+person.link_to_map,'_self');
                        //this is for new tab
                        //'_blank');
                        /*if(win){
                            win.focus();
                        }else{
                            alert('Please allow popups for this site');
                        }*/
                    }
                  })
                  .on('wheel.zoom', function(){
                    //d3.event.stopPropagation();
                  })
                  .on('contextmenu', function(person){
                    d3.event.preventDefault();
                    if(person.type=="matrix_equation")
                        return;
                    if(!person.attributes.extra || person.attributes.extra.length == 0)
                        $(document).trigger("load_details",person);
                    revealPerson(person);
                  })
                  /*.on('mouseout', function(person){
                    revealPerson(person);
                  })*/;
                // Draw the rectangle person boxes.
                // Start new boxes with 0 size so that
                // we can transition them to their proper size.
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
                // Draw the person's name and position it inside the box
                /*nodeEnter.append("text")
                  .attr("dx", 0)
                  .attr("dy", 0)
                  .attr("text-anchor", "start")
                  .attr('class', 'name')
                  .text(function(d) {
                    var text = attributesToString(d.attributes);
                    return text;
                  })
                  .style('fill-opacity', 0);*/
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
                            else if(d.attributes.min){
                                text=minAttributesToString(d)
                            }
                            else if(d.type=="matrix_equation"){
                                text = attributesToEquation(d.attributes);
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
                if(!links || links.length==0)
                    return;

                var self = this;

                var link = svg.selectAll(".link.additional")
                    .data(links, function(d){ return d.id; });

                var newlink = link.enter().insert("g",":first-child")
                    .attr("class", "link additional");
                newlink.append("path")
                  .attr("d", function(d) {
                    var o = {x: 0, y: 0};
                    return transitionElbow({source: o, target: o});
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
                    .transition()
                    .duration(duration)
                    .remove();

                link_remove.select("path")
                  .attr("d", function(d) {
                    var o = {x: 0, y:0};
                    return transitionElbow({source: o, target: o});
                  });

                link_remove.select("text")
                    .attr("transform", function(d) {
                        return "translate(" +
                            0 + "," +
                            0 + ")";
                    });

            },
            drawDetails = function (){
                if(!details_obj||!details_obj.attributes.extra)
                    return;
                var details = svg.select("g.details"),
                    width=0,
                    height=0;
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
                    if(level_info.autorevealing)
                        return;
                    if(person.collapsed||(person._parents.length==0)){
                        $(document).trigger("load_neighbours",person);
                        person.collapsed = false;
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
                person.revealed = false;
                drawDetails();
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
            if(person._parents){
                person._parents.forEach(collapse);
            }
            if(person._children){
                person._children.forEach(collapse);
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
    function attributesToEquation(attributes){
        var text = "";
        text += "<table><tr><td>";
        text += matrixToTable(attributes[0]);
        text += "</td><td>=</td><td>";
        text += matrixToTable(attributes[1]);
        text += "</td><td>x</td><td>";
        text += matrixToTable(attributes[2]);
        text += "</td></tr></table><table><tr><td>";
        text += matrixToTable(attributes[3]);
        text += "</td><td>=</td><td>";
        text += matrixToTable(attributes[4]);
        text += "</td><td>x</td><td>";
        text += matrixToTable(attributes[5]);
        text += "</td></tr></table>";
        return text;
    };
    function matrixToTable(matrix){
        var matrixtype = (typeof(matrix[0])=="string") ? "vector":"matrix";
        var table = "<table class='matrix'><tr><td>";
        matrix.forEach(function(row){
            if(matrixtype == "vector"){
                table += row+"</td></tr><tr><td>";
            }
            else{
                row.forEach(function(item){
                    table += item+"</td><td>";
                })
                table += "</td></tr><tr><td>"
            }
        });
        table += "</td></tr></table>";
        return table;
    };
    function movePerson(person,shift){
        if(person.coord){
            person.coord = [person.coord[0]+shift[0],person.coord[1]+shift[1]];
            console.log(person);
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