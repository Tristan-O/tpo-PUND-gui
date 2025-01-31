$(document).ready(async function() {

    let state = await eel.py_update_state()();
    state.children.forEach(tab => {
        add_tab(tab.name, tab.id, async function() {
            for (let i = 0; i < 2; i++) {
                const wfblocklist = tab.children[i];
                wfblocklist.children.forEach(wfblock => {
                    add_wf_block(tab.id, i+1, wfblock._type)
                });
            }
            await refresh_wf_preview(tab.id)
        });
    });

    let rsrcs = await eel.py_get_available_resources()();
    for (let index = 0; index < rsrcs.length; index++) {
        $('#available-resources').append(`<option>${rsrcs[index]}</option>`)
    }





    class Node {
        constructor($obj, childClass) {
            this.$obj = $obj
            this.childClass = childClass
        }
        find_children() {
            if (this.childClass === null) {return;}
            let children = this.$obj.find(`.${this.childClass}`)
            Array.from(children, element=> Node(element, this.childClass))
            children.forEach(element => {
                element.find_children()
            });
        }
    }

    class Tab extends Node {
        childClass = 'device-settings';
        constructor($obj, id, name) {
            super($obj)
            this.id = id;
            this.name = name;
            this.children = [];
        }
    }

    class Device extends Node {
        childClass = null;
        constructor(name) {
            this.name = name;
        }
    }

    
    function buildDomTree(element, classList) {
        if (!element) return null;
    
        const elementClassList = Array.from(element.classList);
        console.log(elementClassList)
        const matchedClasses = elementClassList.filter(cls => classList.includes(cls));
        console.log(matchedClasses)
    
        if (matchedClasses.length === 0) {
            // If no class matches, skip this element and its children
            return null;
        }
    
        let node = new Node(element.tagName, matchedClasses);
    
        for (let child of element.children) {
            let childNode = buildDomTree(child, classList);
            if (childNode) {
                node.children.push(childNode);
            }
        }
    
        return node;
    }
    
    // Usage example:
    let classList = ['tab-pane', 'waveform-block'];
    let rootElement = document.documentElement; // Starting from the root <html> element
    let domTree = buildDomTree(rootElement, classList);
    
    console.log(JSON.stringify(domTree, null, 2));

});

