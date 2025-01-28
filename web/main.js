$(document).ready(function() {
    
    // Add new tab
    $('#add-tab').click(function() {
        let msg = 'Enter a name for the new tab:'
        let tabName, newTabId
        while (true) {
            tabName = prompt(msg);
            newTabId = tabName.replace(/\s+/g, '-').toLowerCase();
            if (!tabName) {return;}
            else if (/^[A-Za-z][A-Za-z0-9-_]*$/.test(newTabId)) {
                break;
            }
            else {
                msg = `Invalid name ${tabName} (produced id ${newTabId}).\nEnter a name for the new tab:`;
            }
        }

        // Add new tab
        $(`
            <li class="nav-item">
                <a class="nav-link" data-toggle="tab" href="#${newTabId}">
                    ${tabName}
                    <span class="close-tab-btn"><i class="bi bi-x"></i></span>
                </a>
            </li>
        `).insertBefore($(this).parent());

        // Add new tab content
        $('#tab-content').append(`
            <div id="${newTabId}" class="tab-pane fade">
                <div class="tab-content-wrapper"></div>
            </div>
        `);

        // Load template content into new tab
        $(`#${newTabId} .tab-content-wrapper`).load('tab.html', function() {
            eel.py_new_tab(newTabId, tabName)();
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
