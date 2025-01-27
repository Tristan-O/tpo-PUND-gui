$(document).ready(function() {

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
        eel.py_new_tab(newTabId, tabName)();
        // Activate new tab
        $(`a[href="#${newTabId}"]`).tab('show');
        
        // plotly plot
        var data = [{
            x: [1, 2, 3],
            y: [4, 1, 2],
            type: 'scatter'
        }];
        
        // Layout for the plot
        var layout = {
            title: 'Plotly Plot'
        };
        
        // Render the plot
        Plotly.newPlot($(`#${newTabId} .waveform-preview`)[0], data, layout);
    });
});


// All .close-tab-btns will execute this when clicked, even if they are dynamically created
$('#tab-list').on('click', '.close-tab-btn', function() {
    let tabSelector = $(this).parent().attr('href');
    $(this).closest('li').remove();
    eel.py_close_tab($(tabSelector).attr('id'))();
    $(tabSelector).remove();
});


// Dropdowns add blocks
$('#tab-content').on('click', 'select.waveform-block-adder', function() {
    $(this).change(function() {
        const wfType = $(this).val();
        if (wfType) {
            const tabId = get_enclosing_tab_id($(this));
            const channel = $(this).closest('.awg-settings').data('channel');
        
            const $newBlock = $('<div class="waveform-block"></div>')

            $(this).closest('.awg-settings').find('.waveform-block-wrapper').append($newBlock);
            eel.py_new_wf_block(tabId, channel, wfType);
            $newBlock.load('waveform-block.html', function() {
                $newBlock.find('.type-waveform-block').text(wfType);
            }); // the things in this function occur AFTER the loading has finished.
                
            $(this).val(''); // reset selector
        }
    });
});


$('#tab-content').on('click', '.waveform-block i.delete-waveform-block', function() {
    console.log("delete clicked!");
    let $wfBlock = $(this).closest('.waveform-block');
    const tabId = get_enclosing_tab_id($wfBlock);
    const channel = $wfBlock.closest('.awg-settings').data('channel');
    const blockIdx = $wfBlock.index();
    
    eel.py_delete_wf_block(tabId, channel, blockIdx);
    $wfBlock.remove();
});


$('#tab-content').on('click', '.waveform-block i.edit-waveform-block', async function() {
    const tabId = get_enclosing_tab_id($(this));
    const channel = $(this).closest('.awg-settings').data('channel');
    const wfType = $(this).closest('.waveform-block').find('.type-waveform-block').text();
    const blockIdx = $(this).closest('.waveform-block').index();

    console.log("edit clicked!", tabId, channel, blockIdx, wfType);
    let blockSettings = await eel.py_get_wf_block_settings(tabId, channel, blockIdx)();
    let popup = $(`#design-${wfType}`);
    for (const [key, value] of Object.entries(blockSettings)) {
        $(`#${key}-${wfType}`).val(value);
    };
    popup.css('display', 'flex');

    popup.find('.accept-waveform-parameters').on('click', async function() {
        console.log(blockSettings)
        for (const [key, value] of Object.entries(blockSettings)) {
            if ($(`#${key}-${wfType}`).length) { // don't change value if key is not an element in the popup, e.g. _type
                blockSettings[key] = $(`#${key}-${wfType}`).val();
            }
        };
        console.log(blockSettings)
        await eel.py_set_wf_block_settings(tabId, channel, blockIdx, blockSettings)();
    })
});


function get_enclosing_tab_id($elem) {
    return $elem.closest('.tab-pane').attr('id');
};

});