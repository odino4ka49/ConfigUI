WEBVEPP.namespace("WEBVEPP.Tree");
WEBVEPP.TreeView = function(model,html_elements,tree){
    var model = model,
        tree = tree,
        path = null,
        pathindex = 1;

    var zoom = d3.behavior.zoom()
        .scaleExtent([.1,1])
        .on('zoom', function(){
            svg.attr("transform", "translate(" + d3.event.translate + ") scale(" + d3.event.scale + ")");
        })
        .translate([400, 200]);
    var svg = d3.select("body").append("svg")
        .attr('width', "100%")
        .attr('height', "100%")
        .call(zoom)
        .append('g')
        .attr("transform", "translate(400,200)");


    var params = {"svg":svg,"selector":'ancestor', "direction":1, "nodeWidth":100, "nodeHeight":250, "duration":0, "separation":1.3, "boxWidth":170, "boxHeight":110, "boxWidthMax":300, "boxHeightMax":300}

    var ancestorTree = WEBVEPP.Tree(params);
        ancestorTree.setChildren(function(person){
        if(person.collapsed){
          return;
        } else if(person._children){
          return person._parents.concat(person._children);
        } else {
            return person._parents;
        }
    });

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
        var ancestorRoot = rootProxy(tree_data);
        ancestorTree.setSettings(model.getTreeSettings());
        ancestorTree.setData(ancestorRoot);
        ancestorTree.recountXY();
        ancestorTree.draw(ancestorRoot);
    };

    function togglePath(){
        if(pathindex<path.length){
            var person = ancestorTree.findObjectById(path[pathindex]);
            if(pathindex==path.length-1){
                //console.log("move",person)
                ancestorTree.moveToStartPosition(person);
                reloadTree();
            }
            ancestorTree.togglePerson(person);
            pathindex++;
        }
    };

    function toggleStartName(){
        var path = location.pathname.split('/');
        var startname = path[3];
        if(startname!=""){
            var person = ancestorTree.findObjectByName(startname);
            if(person){
                ancestorTree.togglePerson(person);
                ancestorTree.moveToStartPosition(person);
            }
        }
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
        path = model.getPath();
        console.log(path);
        togglePath();
        //toggleStartName();
    });

    $(document).on("tree_changed",function(){
        console.log("tree_changed");
        reloadTree();
        togglePath();
    })

    $(document).on("details_loaded",function(){
        reloadTree();
    })

    return {
    };


};
