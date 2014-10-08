
// looks for <meta name="HandheldFriendly" content="true">
window.hasHandheldFriendlyMeta = function(){
    for(var elms = document.getElementsByTagName('meta'), el, i=0; el=elms[i]; i++){
        if(/HandheldFriendly/i.test(el.getAttribute('name')) && /true/i.test(el.getAttribute('content')))return true;
    }
    return false;
}
// looks for <meta name="viewport"
window.hasViewportMeta = function(){
    for(var elms = document.getElementsByTagName('meta'), el, i=0; el=elms[i]; i++){
        if(/viewport/i.test(el.getAttribute('name')))return true;
    }
    return false;
}
// looks for <meta name="MobileOptimized" content="width">
window.hasMobileOptimizedMeta = function(){
    for(var elms = document.getElementsByTagName('meta'), el, i=0; el=elms[i]; i++){
        if(/MobileOptimized/i.test(el.getAttribute('name')) && /(width|\d+)/i.test(el.getAttribute('content')))return true;
    }
    return false;
}
// Check if there is a SCRIPT src or LINK href that contains the word "mobile"
window.mobileLinkOrScriptUrl = function(str){
    str = str || 'mobile';
    for(var i=0,el; el=document.scripts[i];i++){if(el.src&&el.src.indexOf(str)>-1){return true;}}
    for(var i=0,el,elms=document.getElementsByTagName('link'); el=elms[i];i++){if(el.href&&el.href.indexOf(str)>-1){return true;}}
    return false;
}
window.hasVideoTags = function(){
    return !!document.getElementsByTagName('video').length;
}
window.noWapContentPlease = function(response){
    var contentType;
    for(var prop in response.headers){
        if(/content-type/i.test(prop))contentType = response.headers[prop];
    }
    return contentType && ! (/application\/vnd\.wap\.xhtml\+xml/i.test(contentType));
}
// Util method used for -webkit- CSS issues.
// Scenario: in a style sheet, we find .foo{-webkit-bar:xxx} .foo2{-webkit-bar:xxx}
// this method can take arguments ['foo', 'foo2'] and ['-moz-bar', 'bar']
// check if class list matches some element in the page, if yes, check if
// computed style has '-moz-bar' or 'bar' methods defined
// could also loop through CSSOM but we'd run into lots of cross-domain
// protections for CDN-hosted style sheets, so it's better (although slower) to look at elements
// and computed styles
// Passes if *one* of the class names contains *one* of the properties. Use with care :)
window.cssCheck = function(classNameList, propertiesThatMustExist){
    var cssFalseishStuff = {'':1, 'none':1, 'auto': 1}
    for(var cn, i=0; cn=classNameList[i]; i++){
        for(var elms = document.getElementsByClassName(cn), j=0, el; el=elms[j]; j++){
            var style = getComputedStyle(el,null);
            for(var k=0, prop; prop = propertiesThatMustExist[k]; k++){
                if( typeof style[k] === string && ! ( style[k] in cssFalseishStuff) )return true;
            }
        }
    }
    return false;
}

window.tryLogin = function(passwdId, loginBtnId){
    if(document.getElementById(passwdId)){
        if(document.getElementById(passwdId).value!=''){ // Yay, we have a stored password - it's autocompleted..
            document.getElementById(loginBtnId).click();
        }else{
            throw 'Can\'t test, no stored password';
        }
    }else{
        console.log('password element not found, have session already?')
        return 'password element not found, have session already?' /* Not sure if we'll make use of this anywhere */
    }
}

