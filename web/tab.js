$(document).ready(function() {

function get_enclosing_tab_id($elem) {
    return $elem.closest('.tab-pane').attr('id');
}

// Add new tab
$('#add-tab').click(function() {
    const tabName = prompt('Enter a name for the new tab:');
    if (!tabName) return;

    const newTabId = tabName.replace(/\s+/g, '-').toLowerCase();

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

    // Load template content into new tab and set tab number
    $(`#${newTabId} .tab-content-wrapper`).load('tab.html', function() {
        eel.py_new_tab(newTabId, tabName);
        // Activate new tab
        $(`a[href="#${newTabId}"]`).tab('show');
    });
});


// All .close-tab-btns will execute this when clicked, even if they are dynamically created
$('#tab-list').on('click', '.close-tab-btn', function() {
    let tabSelector = $(this).parent().attr('href');
    $(this).closest('li').remove();
    eel.py_close_tab($(tabSelector).attr('id'));
    $(tabSelector).remove();
});


// Dropdowns add blocks
$('#tab-content').on('click', 'select.block-adder', function() {
    let tabId = get_enclosing_tab_id($(this));
    $(this).change(function() {
        const selectedOption = $(this).val();
        const channel = $(this).data('channel');
        
        if (selectedOption) {
            $(this).parent().parent().find('.waveform-block-wrapper').append(
                '<div id="temporary-id-waveform-block" class="waveform-block"></div>'); // make a div with a temporary id
            $('#temporary-id-waveform-block').load('waveform-block.html', function() {
                $('#temporary-id-label').text(selectedOption);
                $('#temporary-id-label').attr('id',''); // clear the id
                $('#temporary-id-waveform-block').on( "click", "i", function( event ) { // this function is called if any i elements that are children of the $(...) are clicked
                    if (event.target.classList.contains("delete")) {
                        console.log("delete clicked!");
                        $(this).closest('.waveform-block').remove();
                    } else if (event.target.classList.contains("edit")) {
                        console.log("edit clicked!");
                        $('#design-pund').css('display', 'flex');
                    } else if (event.target.classList.contains("move-up")) {
                        console.log("move-up clicked!");
                    } else if (event.target.classList.contains("move-down")) {
                        console.log("move-down clicked!");
                    } else {
                        console.log(event.target.classList);
                        console.log("clicked...?");
                    }
                    // TODO Update template WF
                    // eel.py_new_wf_block(tabId:str, channel:int, block_type:str, args_dict:dict):
                    
                });
                $('#temporary-id-waveform-block').attr('id',''); // clear the id
            }); // the things in this function occur AFTER the loading has finished.
                
            $(this).val('');
        }
    });
});

// Function to add element to the channel box
function addWaveformBlockToChannel(waveformBlock, selectedOption) {
}

});