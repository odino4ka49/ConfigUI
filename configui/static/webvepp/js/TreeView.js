WEBVEPP.namespace("WEBVEPP.Tree");
WEBVEPP.TreeView = function(model,html_elements,tree){
    var model = model,
        tree = tree;

    var zoom = d3.behavior.zoom()
        .scaleExtent([.1,1])
        .on('zoom', function(){
            svg.attr("transform", "translate(" + d3.event.translate + ") scale(" + d3.event.scale + ")");
        })
        // Offset so that first pan and zoom does not jump back to the origin
        .translate([400, 200]);
    var svg = d3.select("body").append("svg")
        .attr('width', "100%")
        .attr('height', "100%")
        .call(zoom)
        .append('g')
        // Left padding of tree so that the whole root node is on the screen.
        // TODO: find a better way
        .attr("transform", "translate(400,200)");


    var params = {"svg":svg,"selector":'ancestor', "direction":1, "nodeWidth":100, "nodeHeight":250, "duration":0, "separation":1.3, "boxWidth":170, "boxHeight":110, "boxWidthMax":300, "boxHeightMax":300}

    var ancestorTree = WEBVEPP.Tree(params);
        ancestorTree.setChildren(function(person){
        // If the person is collapsed then tell d3
        // that they don't have any ancestors.
        if(person.collapsed){
          return;
        } else if(person._children){
          return person._parents.concat(person._children);
        } else {
            return person._parents;
        }
    });

    // Use a separate tree to display the descendants
    /*var descendantsTree = WEBVEPP.Tree(params);
        descendantsTree.setChildren(function(person){
        if(person.collapsed){
          return;
        } else {
          return person._children;
        }
    });*/

    function collapse(person){
      person.collapsed = true;
      if(person._parents){
        person._parents.forEach(collapse);
      }
      if(person._children){
        person._children.forEach(collapse);
      }
    }

    function reloadTree(){
        var tree_data = model.getTreeData();

        // D3 modifies the objects by setting properties such as
        // coordinates, parent, and children. Thus the same node
        // node can't exist in two trees. But we need the root to
        // be in both so we create proxy nodes for the root only.
        var ancestorRoot = rootProxy(tree_data);
        //var descendantRoot = rootProxy(tree_data);

        // Start with only the first few generations of ancestors showing
        /*ancestorRoot._parents.forEach(function(parents){
          parents._parents.forEach(collapse);
        });*/

        // Start with only one generation of descendants showing
        //descendantRoot._children.forEach(collapse);

        // Set the root nodes
        ancestorTree.setData(ancestorRoot);
        ancestorTree.setSettings(model.getTreeSettings());
        ancestorTree.recountXY();
        //descendantsTree.data(descendantRoot);

        // Draw the tree
        ancestorTree.draw(ancestorRoot);
        //descendantsTree.draw(descendantRoot);

      //});
      };

    function rootProxy(root){
      return {
        name: root.name,
        id: root.id,
        x0: 0,
        y0: 0,
        width: root.width,
        height: root.height,
        _children: root._children,
        _parents: root._parents,
        collapsed: false,
        attributes: root.attributes,
        additional_links: root.additional_links
      };
    };

    $(document).on("tree_created",function(){
        reloadTree();
    });

    $(document).on("tree_changed",function(){
        reloadTree();//ancestorTree.draw();
    })

    return {
    };


};