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
        tree,
        root,
        details_obj,


        setChildren = function(children){
            tree.children(children);
        },
        setData = function(data){
            root = data;
        },
        draw = function(source){
            if(root){
                var nodes = tree.nodes(root),
                    links = tree.links(nodes);
                drawLinks(links, source);
                drawNodes(nodes, source);
                drawDetails();
            } else {
                //throw new Error('Missing root');
            }
        },
        drawLinks = function(links, source){
            var self = this;

            var link = svg.selectAll("path.link." + selector)
                .data(links, function(d){ return d.target.id; });

            link.enter().append("path")
                .attr("class", "link " + selector)
                .attr("d", function(d) {
                    var o = {x: source.x0, y: direction * (source.y0 + boxWidth/2)};
                    return transitionElbow({source: o, target: o});
                });

            link.transition()
                .duration(duration)
                .attr("d", function(d){
                    return elbow(d, direction);
                });

            link.exit()
                .transition()
                .duration(duration)
                .attr("d", function(d) {
                    var o = {x: source.x, y: direction * (source.y + boxWidth/2)};
                    return transitionElbow({source: o, target: o});
                })
                .remove();
            },
            drawNodes = function(nodes, source){

                var node = svg.selectAll("g.person." + selector)
                  .data(nodes, function(person){ return person.id; });

                // Add any new nodes
                var nodeEnter = node.enter().append("g")
                  .attr("class", "person " + selector)

                  // Add new nodes at the right side of their child's box.
                  // They will be transitioned into their proper position.
                  .attr('transform', function(person){
                    return 'translate(' + (direction * (source.y0 + boxWidth/2)) + ',' + source.x0 + ')';
                  })
                  .on('click', function(person){
                    togglePerson(person);
                  })
                  .on('wheel.zoom', function(){
                    d3.event.stopPropagation();
                  })
                  .on('mouseover', function(person){
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
                            var text = attributesToString(d.attributes.min);
                            text += d.revealed? attributesToString(d.attributes.extra): "";
                            return '<div style="width: '+(boxWidth)+'px; height: '+(boxHeight)+'px" class="attributes">'+text+'</div>'
                        });


                // Update the position of both old and new nodes
                var nodeUpdate = node.transition()
                  .duration(duration)
                  .attr("transform", function(d) { return "translate(" + (direction * d.y) + "," + d.x + ")"; });

                // Grow boxes to their proper size
                nodeUpdate.select('rect')
                  .attr({
                    x: -(boxWidth/2),
                    y: -(boxHeight/2)-5
                  })
                  .attr('width', function(d){
                    return boxWidth;//d.revealed ? boxWidthMax: boxWidth
                  })
                  .attr('height', function(d){
                    return boxHeight;//d.revealed ? boxHeightMax: boxHeight
                  });

                // Move text to it's proper position
                nodeUpdate.select('foreignObject')
                    .attr("x", -(boxWidth/2))
                    .attr("y", -(boxHeight/2))
                    .attr('width', function(d){
                        return boxWidth;//d.revealed ? boxWidthMax: boxWidth
                    })
                    .attr('height', function(d){
                        return boxHeight;//d.revealed ? boxHeightMax: boxHeight
                    })
                    .style('fill-opacity', 1);

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
                  .attr("transform", function(d) { return "translate(" + (direction * (source.y + boxWidth/2)) + "," + source.x + ")"; })
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
                    .attr({
                        x: details_obj.y-(boxWidth/2),
                        y: details_obj.x-(boxHeight/2)-5
                    })
                    .attr('width', function(d){
                        return width;
                    })
                    .attr('height', function(d){
                        return height;
                    });
                details.select("foreignObject")
                    .attr({
                        x: details_obj.y-(boxWidth/2),
                        y: details_obj.x-(boxHeight/2)-5
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
                if(person === this.root){
                    return;
                }
                // Non-root nodes
                else {
                    if(person.collapsed){
                      person.collapsed = false;
                    } else {
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
        .nodeSize([nodeWidth, nodeHeight])
        .separation(function(){
            return separation;
        });
    function newDetailsObj(){
        if(!svg.select("g.details").empty())
            return;
        var det_obj = svg.append("g").attr("class", "details")
            .on("mouseout",function(){
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
    function collapse(person){
        person.collapsed = true;
            if(person._parents){
                person._parents.forEach(collapse);
            }
            if(person._children){
                person._children.forEach(collapse);
        }
    };
    function elbow(d, direction) {
        var sourceX = d.source.x,
          sourceY = d.source.y + (boxWidth / 2),
          targetX = d.target.x,
          targetY = d.target.y - (boxWidth / 2);

        return "M" + (direction * sourceY) + "," + sourceX
        + "H" + (direction * (sourceY + (targetY-sourceY)/2))
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

    return {
        setChildren:setChildren,
        setData:setData,
        draw:draw,
        drawNodes:drawNodes,
        drawLinks:drawLinks,
        togglePerson:togglePerson,
    };
};