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
                var allofus = d.parent._parents;
                d.x = countNodeX(d.depth,allofus.indexOf(d));
            });
        },
        countNodeY = function(node){
            var index,number,
                depth = node.depth,level_name,level_info,
                pos=0;
            if(depth==0){
                return 0;
            }
            var allofus = node.parent._parents;
                index = allofus.indexOf(node);
                number = allofus.length;
                level_name = "level"+depth;
                level_info = settings[level_name].display_attributes;
            if("positioning" in level_info && level_info.positioning=="matrix"){
                var matrix = allofus[allofus.length-1]
                if(index==number-1){
                    return countNodeY(node.parent);
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
            return (10+level_info.height)*(pos)+countNodeY(node.parent);
        },
        countNodeX = function(node){
            var result = 0,
                depth = node.depth,
                index = 0,
                allofus;
            if(node.depth!=0){
                allofus = node.parent._parents;
                index = allofus.indexOf(node);
            }
            for(var i=1;i<=depth;i++){
                var level_name = i==0? "root":"level"+i;
                var level_info = settings[level_name].display_attributes;
                var node_width = level_info.width;
                if("positioning" in level_info && level_info.positioning=="matrix"){
                    var matrix = allofus[allofus.length-1]
                    if(i==depth){
                        if(index==allofus.length-1){
                            return countLevelX(node)-90+matrix.width/2;
                        }
                        result+=(index%matrix.cols)*(node_width+20)-45
                    }
                    else{
                        if("hiding" in level_info && level_info.hiding){
                            var unhidden,d=node;
                            while(d.depth!=i){
                                d = d.parent;
                            }
                            result = countNodeX(d)+50;
                        }
                        else{
                            result += matrix.width*2;
                        }
                    }
                }
                if(i!=depth)
                    result += node_width+50;
            }
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
            var depth = node.depth
            if(depth==0)
                return 0;
            var result = 0;
            for(var i=1;i<depth;i++){
                var level_name = i==0? "root":"level"+i;
                var level_info = settings[level_name].display_attributes;
                var node_width = level_info.width;
                if("positioning" in level_info && level_info.positioning=="matrix"){
                    if("hiding" in level_info && level_info.hiding){
                        var unhidden,d=node;
                        while(d.depth!=i){
                            d = d.parent;
                        }
                        result += countNodeX(d)+50;
                    }
                    else{
                        var columns = (level_info.matrix_size>16)? 8:4;
                        result += (node_width+30)*columns;
                    }
                }
                result += node_width+50;
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
            person.parent._parents.forEach(function(sibling){
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
            }
        },
        removeAdditionalLink = function(link){
            root.additional_links.splice(root.additional_links.indexOf(link),1);
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
                    return elbow(d, direction);
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
                  })
                  .on('wheel.zoom', function(){
                    d3.event.stopPropagation();
                  })
                  .on('contextmenu', function(person){
                    d3.event.preventDefault();
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
                        .append("xhtml:body")
                        .html(function(d){
                            var text = (d.width>100) ? attributesToString(d.attributes.min): attributesToShortString(d.attributes.min);
                            //text += d.revealed? attributesToString(d.attributes.extra): "";
                            return '<div style="width: '+(d.width)+'px; height: '+(d.height)+'px" class="attributes">'+text+'</div>'
                        })
                      .attr("class",function(d){
                        return countNodeClass(d);
                      });


                // Update the position of both old and new nodes
                var nodeUpdate = node.transition()
                  .duration(duration)
                  .attr("transform", function(d) { return "translate(" + (direction * d.y) + "," + d.x + ")"; });

                // Grow boxes to their proper size
                nodeUpdate.select('rect')
                  .attr('x',function(d){
                    if(d.depth==0)
                        return 0;
                    var x = countNodeX(d);
                    return x-(d.width/2);
                  })
                  .attr('y',function(d){
                    if(d.depth==0)
                        return 0;
                    var y = countNodeY(d);
                    return y-(d.height/2)-5;
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
                        var x = countNodeX(d);
                        return x-(d.width/2);
                    })
                    .attr("y", function(d){
                        if(d.depth==0)
                            return 0;
                        var y = countNodeY(d);
                        return y-(d.height/2)-5;
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
                  });

                /*node.select('foreignObject')
                    .select("body")
                    .html(function(d){
                            var text = attributesToString(d.attributes.min);
                            var width = d.revealed ? boxWidthMax: boxWidth,
                                height = d.revealed ? boxHeightMax: boxHeight;
                            text += d.revealed? attributesToString(d.attributes.extra): "";
                            return '<div style="width: '+(width)+'px; height: '+(height)+'px" class="attributes">'+text+'</div>'
                        });*/
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
                            return backward_elbow(d, direction);
                        }
                        else{
                            removeAdditionalLink(d);
                            link_update.remove();
                        }
                    });

                link_update.select("text")
                    .attr("transform", function(d) {
                        if(d.source && d.target)
                            return "translate(" +
                            (countNodeX(d.target)+d.target.width/2+10) + "," +
                            (countNodeY(d.target)-5) + ")";
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
                if(!details_obj)
                    return;
                var details = svg.select("g.details"),
                    width=0,
                    height=0;
                if(details_obj.revealed){
                    width = boxWidthMax;
                    height = boxHeightMax;
                }
                details.select("rect")
                    .attr('x',function(d){
                        return countNodeX(details_obj)-(width/2)
                    })
                    .attr('y',function(d){
                        return countNodeY(details_obj)-(height/2)-5
                    })
                    .attr('width', function(d){
                        return width;
                    })
                    .attr('height', function(d){
                        return height;
                    });
                details.select("foreignObject")
                    .attr('x',function(d){
                        return countNodeX(details_obj)-(width/2)
                    })
                    .attr('y',function(d){
                        return countNodeY(details_obj)-(height/2)
                    })
                    .attr('width', function(d){
                        return width;
                    })
                    .attr('height', function(d){
                        return height;
                    })
                    .select("body")
                    .html(function(){
                        var text = attributesToString(details_obj.attributes.min.concat(details_obj.attributes.extra));
                        return '<div style="width: '+(width)+'px; height: '+(height)+'px" class="attributes">'+text+'</div>'
                    })
            },
            togglePerson = function(person){
                // Don't allow the root to be collapsed because that's
                // silly (it also makes our life easier)
                if(person.depth<1 || isMatrix(person)){
                    return;
                }
                // Non-root nodes
                else {
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
            }
            revealPerson = function(person){
                person.revealed = !person.revealed;
                details_obj = person;
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
        var sourceX = countNodeY(d.source),
        sourceY = countNodeX(d.source) + (d.source.width / 2),
        targetX = countNodeY(d.target),
        targetY = countNodeX(d.target) - (d.target.width / 2),
        target_levelY = countLevelX(d.target) - (d.target.width / 2);

        if(d.source.depth!=0){
            var level_info = settings["level"+d.target.depth].display_attributes;
            if("positioning" in level_info && level_info.positioning=="matrix"){
                return "M" + (direction * sourceY) + "," + sourceX + "H" + (direction * targetY);
            }
        }

        return "M" + (direction * sourceY) + "," + sourceX
        + "H" + (direction * (sourceY + (target_levelY-sourceY)/2))
        + "V" + targetX
        + "H" + (direction * targetY);
    };
    function backward_elbow(d,direction) {
        var sourceX = countNodeY(d.source),
        sourceY = countNodeX(d.source) - (d.source.width / 2),
        targetX = countNodeY(d.target),
        targetY = countNodeX(d.target) + (d.target.width / 2),
        target_levelY = countLevelX(d.target) + (d.target.width / 2);

        if(sourceY==target_levelY - d.target.width ){
            target_levelY = target_levelY + d.source.width+50;
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
    function attributesToString(attributes){
        var text = "";
        attributes.forEach(function(attr){
            text += attr.key+": "+attr.value+"<br/>";
        });
        return text;
    };
    function attributesToShortString(attributes){
        var text = "";
        attributes.forEach(function(attr){
            if(attr.key=="Index"){
                text += "<div style='display: inline-table;'>" + attr.value+"</div><div style='display: inline-table; margin-left:5px'>";
            }
            else{
                text += attr.value+"<br/>";
            }
        });
        text += "</div>";
        return text;
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
    };
};