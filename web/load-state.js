$(document).ready(async function() {

    let state = await eel.py_update_state()();
    state.children.forEach(tab => {
        add_tab(tab.name, tab.id, async function() {
            for (let i = 0; i < tab.children.length; i++) {
                for (let j = 0; j < tab.children[i].children.length; j++) {
                    console.log( tab.children[i] )
                }
                // const wfblocklist = tab.children[i];
                // wfblocklist.children.forEach(wfblock => {
                    // add_wf_block(tab.id, i+1, wfblock._type)
                // });
            }
            // await refresh_wf_preview(tab.id)
        });
    });

    let rsrcs = await eel.py_get_available_resources()();
    for (let index = 0; index < rsrcs.length; index++) {
        $('#available-resources').append(`<option>${rsrcs[index]}</option>`)
    }


});

