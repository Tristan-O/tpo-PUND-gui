$(document).ready(function() {
    
    // Add new tab
    $('#add-tab').click(function() {
        let msg = 'Enter a name for the new tab:'
        let newTabName, newTabId
        while (true) {
            newTabName = prompt(msg);
            newTabId = newTabName.replace(/\s+/g, '-').toLowerCase();;
            if (!newTabName) {return;}
            else if (/^[A-Za-z][A-Za-z0-9-_]*$/.test(newTabId)) {
                break;
            }
            else {
                msg = `Invalid name ${newTabName} (produced id ${newTabId}).\nEnter a name for the new tab:`;
            }
        }
        add_tab(newTabName, newTabId, function() {
            // Register new tab with python
            eel.py_new_tab(newTabId, newTabName)();
            // Activate new tab
            $(`a[href="#${newTabId}"]`).tab('show');
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
        <div id="${newTabId}" class="tab-pane fade">
            <div class="tab-content-wrapper"></div>
        </div>
    `);

    // Load template content into new tab
    $(`#${newTabId} .tab-content-wrapper`).load('tab.html', func_on_loaded);
};
