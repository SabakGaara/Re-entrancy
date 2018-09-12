function analyze_solidity(){
    document.getElementById("start_button_1").innerHTML="<strong>Analyzing</strong>";
    var type="solidity";
    var name=document.getElementById("solidity_name").value;
    var target=document.getElementById("target_depth").value;
    var owner=document.getElementById("target_depth").value;
    var code=editor.getValue();
    httpPost(type, name, code, target,owner);
}

function analyze_bytecode(){
    document.getElementById("start_button_2").innerHTML="<strong>Analyzing</strong>";
    var type="bytecode";
    var name="";
    var target=document.getElementById("target_depth").value;
    var owner=document.getElementById("owner_depth").value;
    var code=document.getElementById("bytecode").value;
    httpPost(type, name, code, target,owner);
}


function httpPost(type, name, code,target,owner) {
    var xmlhttp;
    xmlhttp=null;
    if (window.XMLHttpRequest)
    {
        // code for all new browsers
        xmlhttp=new XMLHttpRequest();
    }
    else if (window.ActiveXObject)
    {
        // code for IE5 and IE6
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    if (xmlhttp!=null)
    {
        xmlhttp.onreadystatechange=state_Change;
        xmlhttp.open("post","http://39.106.37.208:5000/api/analyze",true);
        //var content = "type="+type+"&code="+code+"&input="+input;
        var formData = new FormData();
        formData.append("type", type);
        formData.append("name", name);
        formData.append("code", code);
        formData.append("target",target);
        formData.append("owner",owner);
        xmlhttp.send(formData);
    }
    else
    {
        alert("Your browser does not support XMLHTTP.");
    }

    function state_Change(){
        document.getElementById("start_button_1").innerHTML="<strong>Click HERE to Start Analyzing!</strong>";
        document.getElementById("start_button_2").innerHTML="<strong>Click HERE to Start Analyzing!</strong>";
        if (xmlhttp.readyState==4)
        {
            // 4 = "loaded"
            if (xmlhttp.status==200)
            {
                // 200 = OK
                // alert(xmlhttp.responseText);
                var result=xmlhttp.responseText;
                if (result.indexOf("Reentrancy")!=-1)
                {
                    var result_show="<p><p style = 'color:red;font-weight: 700'>Analysis Log: Reentrancy bug</p>"+result.replace(/[\n\r]/g,'<br>')+"</p>";
                }
                else 
                {
                    var result_show="<p><p style = 'font-weight: 700'>Analysis Log:</p>"+result.replace(/[\n\r]/g,'<br>')+"</p>";
                }
                
                result_show+='</div>  </div></div>';
                document.getElementById("analyze_result").innerHTML=result_show;
            }
            else
            {
                alert("Problem retrieving XML data");
            }
        }

    }
}


