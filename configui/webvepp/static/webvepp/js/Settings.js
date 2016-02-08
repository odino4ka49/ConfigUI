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

    $(document).on("save_settings",function(event,d){
        system_name = document.getElementById("settings_system_name").value;
        $(document).trigger("set_cookie",["system_name",system_name]);
    });

    return {
        getSystemName: getSystemName,
    };
};

function saveSettings(){
    $(document).trigger("save_settings");
}

