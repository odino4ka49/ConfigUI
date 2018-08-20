WEBVEPP.namespace("WEBVEPP.Settings");
WEBVEPP.Settings = function(cookies){
    var system_name,
        cookies = cookies;

    function getSystemName(){
        system_name = cookies.get("system_name");
        if(!system_name){
            $(document).trigger("set_cookie",["system_name","CHAN"]);
            system_name = "CHAN";
        }
        return system_name;
    };

    function setSystem(){
        settings_system = document.getElementById("settings_system_name");
        system_name = cookies.get("system_name");
        settings_system.value = system_name;
    };

    function reloadLocation(){
        var path = location.pathname.split("/");
        location.pathname = path[1]+"/"+path[2];
        //location.reload();
    };

    $(document).on("save_settings",function(event,d){
        system_name = document.getElementById("settings_system_name").value;
        $(document).trigger("set_cookie",["system_name",system_name]);
        reloadLocation();
    });
    $(document).on("switch_system",function(event,name){
        system_name = name;
        document.getElementById("settings_system_name").value = system_name;
        $(document).trigger("set_cookie",["system_name",system_name]);
        reloadLocation();
    });

    setSystem();

    return {
        getSystemName: getSystemName,
    };
};

function saveSettings(){
    $(document).trigger("save_settings");
}

