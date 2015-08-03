(function(){
    /*
    Analyses applied CSS and sums up findings
    We want to return a list of objects referring to elements
    in the page with the following details:
        selector: a CSS selector that will match the element (not necessarily the one in the CSS)
        index: the index of the element in the selection you get
               if you do document.querySelectorAll(selector)
        coords: {x: y: width: height: }
        problems: [ {property: value: } ]
    */
    /*TODO:

    Perhaps unsurprising, a major issue with this approach is performance.
    It might not seem like a big problem for something that can run by itself
    and record data at leisure, but slow performance makes it time consuming to
    test and develop..

    */

    var ts1 = new Date;
    var list = [];
    var neutralFrame = document.body.appendChild(document.createElement('iframe'));
    var comparisonStyle = cloneobj(neutralFrame.contentWindow.getComputedStyle(neutralFrame.contentDocument.body));
    document.body.removeChild(neutralFrame);
    console.log('Before qsa' + ((new Date)-ts1));
    var elms = document.querySelectorAll('*');
    var css_properties = ['webkitAnimation', 'webkitTransition', 'webkitTransform'];
    var css_values = ['-webkit-gradient', '-webkit-flex', '-webkit-box'];
    for (var i =0, elm;  elm = elms[i]; i++) {
        console.log('Før elm: ' + elm.tagName + ' ' + ((new Date)-ts1));
        var coords = elm.getBoundingClientRect();
        var tmp = createCSSSelector(elm);
        var obj = {selector:tmp[0].join(' '), index: tmp[1], coords: cloneobj(coords), problems: []}
//        console.log(elm.outerHTML.substr(0,30) +' ' + JSON.stringify(obj));
        var style = getComputedStyle(elm);
        // property test
        for(var j = 0, css; css = css_properties[j]; j++){
            // This is where we should figure out if the value is set or default..
            if(style[css] !== comparisonStyle[css]){
                obj.problems.push({property:css, value: style[css]});
            }
        }
        // value test
        for(var prop in style){
            if(isNaN(parseInt(prop)) && prop !== 'cssText'){// We skip the numerical lists of properties
                for(var j = 0, css; css = css_values[j]; j++){
                    if(style[prop] && style[prop].toString().indexOf(css) > -1){
                        obj.problems.push({property: prop, value: style[prop]});
                    }
                }
            }
        }

        if(obj.problems.length){
            list.push(obj);
        }
        console.log((new Date)-ts1);
    };
    return JSON.stringify(list, null, 2);

    function createCSSSelector(elm){
        var desc = '', descParts = [], origElm = elm;
        while(elm){
            descParts.unshift(descElm(elm));
            desc = descParts.join(' ');
            if(document.querySelectorAll(desc).length === 1 || descParts.length > 5){
                break;
            }
            elm = elm.parentElement;
        }
        var elms = document.querySelectorAll(desc), idx;
        for(var i = 0; i<elms.length; i++){
            if(elms[i] === origElm){
                idx = i;
                break;
            }
        }
        return [descParts, i];
    }

    function descElm(elm){
        var desc = elm.tagName.toLowerCase();
        if(elm.id){
            desc += '#' + elm.id;
        }
        if(elm.className){
            desc += '.' + [].join.call(elm.classList, '.');
        }
        if(elm.href){
            desc += '[href="' + elm.href + '"]';
        }
        return desc;
    }

    function cloneobj(rect){
        var obj = {};
        for(var prop in rect){
            obj[prop] = rect[prop];
        }
        return obj;
    }

}
)()
