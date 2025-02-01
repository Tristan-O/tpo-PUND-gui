$(document).ready(function() {
    
    // Add new tab
    $('#add-tab').click(async function() {
        let msg = 'Enter a name for the new tab:'
        let newTabName, newTabId
        while (true) {
            newTabName = prompt(msg);
            newTabId = newTabName.replace(/\s+/g, '-').toLowerCase();;
            if (!newTabName) {return;}
            else if ($(`#${newTabId}`).length != 0) {
                msg = `Invalid name ${newTabName} (produced id ${newTabId}, which already exists).\nEnter a name for the new tab:`;
            } else if (/^[A-Za-z][A-Za-z0-9-_]*$/.test(newTabId)) {break;}
            else {
                msg = `Invalid name ${newTabName} (produced id ${newTabId}).\nEnter a name for the new tab:`;
            }
        }
        add_tab(newTabName, newTabId, async function() {
            // Register new tab with python
            py_id = await eel.py_new_tab(newTabId, newTabName)();
            $(`#${newTabId}`).data('py_id', py_id)
            // Activate new tab
            $(`a[href="#${newTabId}"]`).tab('show');

            await eel.py_update_frontend(py_id)();
            const $awg = $(`#${newTabId}`).find('[data-pyclassname="AWGSettings"]');
            await refresh_wf_preview( $(`#${newTabId}`).find('[data-pyclassname="AWGSettings"]') );
        });
    });

    // Connect to instruments
    $('#connect-btn').click(function() {
        eel.py_connect();
    });
    
    // Trigger Instruments
    $('#trigger-btn').click(function() {
        eel.py_trigger();
    });

    // Close a popup waveform editor
    $('.close-popup-btn').click(function() {
        $('.popup').css('display', 'none');
    })

});

function add_tab(newTabName, newTabId, func_on_loaded) {
    // Add new tab
    $(`
        <li class="nav-item">
            <a class="nav-link" data-toggle="tab" href="#${newTabId}">
                ${newTabName}
                <span class="close-tab-btn"><i class="bi bi-x"></i></span>
            </a>
        </li>
    `).insertBefore($('#add-tab').closest('li'));

    // Add new tab content
    $('#tab-content').append(`
        <div id="${newTabId}" class="tab-pane fade" data-py_id="" data-pyclassname="Tab">
            <div class="tab-content-wrapper"></div>
        </div>
    `);

    // Load template content into new tab
    $(`#${newTabId} .tab-content-wrapper`).load('tab.html', func_on_loaded);
};


eel.expose(js_update_frontend);
function js_update_frontend(element_selector, params) {
    const $elem = $(element_selector);
    // console.log(element_selector, $elem)
    for (const [key, value] of Object.entries(params)) {
        $paramElem = $elem.data(key, value);
        // Find the inputs that control those, if any, and update them
    };
    // console.log(element_selector, $elem.data('py_id'), params)
}
