$(document).ready(function() {

// Close tab
// All .close-tab-btns will execute this when clicked, even if they are dynamically created
$('#tab-list').on('click', '.close-tab-btn', function() {
    let tabSelector = $(this).parent().attr('href');
    let thisIdx = $(this).closest('li').index();
    $('#analysis-tab').tab('show');
    $('#tab-list').find('a')[0].click();
    console.log(thisIdx)
    console.log( $($('#tab-list').find('li')[thisIdx-1]).find('a') )

    $(this).closest('li').remove();
    eel.py_close_tab($(tabSelector).attr('id'))();
    $(tabSelector).remove();
});


// Dropdowns add waveform blocks
$('#tab-content').on('click', 'select.waveform-block-adder', function() {
    $(this).change( async function() {
        const wfType = $(this).val();
        if (wfType) {
            const tabId = get_enclosing_tab_id($(this));
            const channel = $(this).closest('.awg-settings').data('channel');
        
            const $newBlock = $('<div class="waveform-block"></div>')

            $(this).closest('.awg-settings').find('.waveform-block-wrapper').append($newBlock);
            eel.py_new_wf_block(tabId, channel, wfType)();
            $newBlock.load('waveform-block.html', function() {
                $newBlock.find('.type-waveform-block').text(wfType);
            }); // the things in this function occur AFTER the loading has finished.
                
            $(this).val(''); // reset selector

            await refresh_wf_preview(tabId);
        }
    });
});


// Delete waveform block
$('#tab-content').on('click', '.waveform-block i.delete-waveform-block', function() {
    console.log("delete clicked!");
    let $wfBlock = $(this).closest('.waveform-block');
    const tabId = get_enclosing_tab_id($wfBlock);
    const channel = $wfBlock.closest('.awg-settings').data('channel');
    const blockIdx = $wfBlock.index();
    
    eel.py_delete_wf_block(tabId, channel, blockIdx);
    $wfBlock.remove();
});


// Edit waveform block
$('#tab-content').on('click', '.waveform-block i.edit-waveform-block', async function() {
    const tabId = get_enclosing_tab_id($(this));
    const channel = $(this).closest('.awg-settings').data('channel');
    const wfType = $(this).closest('.waveform-block').find('.type-waveform-block').text();
    const blockIdx = $(this).closest('.waveform-block').index();

    console.log("edit clicked!", tabId, channel, blockIdx, wfType);
    let blockSettings = await eel.py_get_wf_block_settings(tabId, channel, blockIdx)();
    let popup = $(`#editor-${wfType}`);
    for (const [key, value] of Object.entries(blockSettings)) {
        popup.find(`.waveform-parameter[name=${key}]`).val(value);
    };
    popup.css('display', 'flex');

    // Tie popup actions to this particular block
    popup.find('.accept-waveform-parameters').off('click')
    popup.find('.accept-waveform-parameters').on('click', async function() {
        console.log(blockSettings)
        for (const [key, value] of Object.entries(blockSettings)) {
            if (popup.find(`.waveform-parameter[name=${key}]`).length) { // don't change value if key is not an element in the popup, e.g. _type
                blockSettings[key] = parseFloat(popup.find(`.waveform-parameter[name=${key}]`).val());
            }
        };
        console.log(blockSettings)
        await eel.py_set_wf_block_settings(tabId, channel, blockIdx, blockSettings)();
        await refresh_wf_preview(tabId);
        popup.css('display', 'none');
    })
});


// Upload waveform
$('#tab-content').on('click', '.waveform-upload', async function() {
    const tabId = get_enclosing_tab_id($(this));
    let success = await eel.py_upload_waveform(tabId)();
    if (success) {
        $('.waveform-upload').removeClass('btn-success')
        $(this).addClass('btn-success')
    }
});


function get_enclosing_tab_id($elem) {
    return $elem.closest('.tab-pane').attr('id');
};

async function refresh_wf_preview(tabId) {
    let data = await eel.py_get_wf_skeleton(tabId)();

    let layout = {
        title: 'Waveform Preview'
    };
    
    console.log(data)
    Plotly.newPlot($(`#${tabId} .waveform-preview`)[0], data, layout);
}

});