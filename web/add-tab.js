$(document).ready(function() {

    // Close tab
    // All .close-tab-btns will execute this when clicked, even if they are dynamically created
    $('#tab-list').on('click', '.close-tab-btn', function() {
        let tabSelector = $(this).parent().attr('href');
        let thisIdx = $(this).closest('li').index();
        $('#analysis-tab').tab('show');
        $('#tab-list').find('a')[0].click();

        $(this).closest('li').remove();
        eel.py_close_tab($(tabSelector).attr('id'))();
        $(tabSelector).remove();
    });


    // Dropdowns add waveform blocks
    $('#tab-content').on('change', 'select.waveform-block-adder', async function() {
        const wfType = $(this).val();
        if (wfType) {
            const tabId = get_enclosing_tab_id($(this));
            const channel = $(this).closest('.awg-settings').data('channel');
        
            eel.py_new_wf_block(tabId, channel, wfType)();
            await refresh_wf_preview(tabId);

            add_wf_block(tabId, channel, wfType)

            $(this).val(''); // reset selector
        }
    });

    // Delete waveform block
    $('#tab-content').on('click', '.waveform-block i.delete-waveform-block', async function() {
        console.log("delete clicked!");

        let $wfBlock = $(this).closest('.waveform-block');
        const tabId = get_enclosing_tab_id($wfBlock);
        const channel = $wfBlock.closest('.awg-settings').data('channel');
        const blockIdx = $wfBlock.index();
        
        await eel.py_delete_wf_block(tabId, channel, blockIdx)();
        $wfBlock.remove();

        await refresh_wf_preview(tabId);
    });


    // Edit waveform block
    $('#tab-content').on('click', '.waveform-block i.edit-waveform-block', async function() {
        console.log("edit clicked!");

        const tabId = get_enclosing_tab_id($(this));
        const channel = $(this).closest('.awg-settings').data('channel');
        const wfType = $(this).closest('.waveform-block').data('wftype');
        const blockIdx = $(this).closest('.waveform-block').index();

        let blockSettings = await eel.py_get_wf_block_settings(tabId, channel, blockIdx)();
        let popup = $(`#editor-${wfType}`);
        for (const [key, value] of Object.entries(blockSettings)) {
            popup.find(`.waveform-parameter[name=${key}]`).val(value);
        };
        popup.css('display', 'flex');

        // Tie popup actions to this particular block
        popup.find('.accept-waveform-parameters').off('click')
        popup.find('.accept-waveform-parameters').on('click', async function() {
            for (const [key, value] of Object.entries(blockSettings)) {
                if (popup.find(`.waveform-parameter[name=${key}]`).length) { // don't change value if key is not an element in the popup, e.g. _type
                    blockSettings[key] = parseFloat(popup.find(`.waveform-parameter[name=${key}]`).val());
                }
            };
            await eel.py_set_wf_block_settings(tabId, channel, blockIdx, blockSettings)();
            await refresh_wf_preview(tabId);
            popup.css('display', 'none');
        })
    });

    // Move-up waveform block
    $('#tab-content').on('click', '.waveform-block i.move-up-waveform-block', async function() {
        console.log("move-up clicked!");
        let $wfBlock = $(this).closest('.waveform-block');
        let $parent = $wfBlock.parent()
        const tabId = get_enclosing_tab_id($wfBlock);
        const channel = $wfBlock.closest('.awg-settings').data('channel');
        const blockIdx = $wfBlock.index();
        
        if (blockIdx < 1 || blockIdx >= $parent.children().length) {
            console.log("Invalid index");
            return;
        }
        
        let $upperChild = $($parent.children()[blockIdx - 1]);
        $wfBlock.insertBefore($upperChild);
          
        await eel.py_swap_wf_blocks(tabId, channel, blockIdx, blockIdx-1)();

        await refresh_wf_preview(tabId);
    });

    // Move-up waveform block
    $('#tab-content').on('click', '.waveform-block i.move-down-waveform-block', async function() {
        console.log("move-down clicked!");
        let $wfBlock = $(this).closest('.waveform-block');
        let $parent = $wfBlock.parent()
        const tabId = get_enclosing_tab_id($wfBlock);
        const channel = $wfBlock.closest('.awg-settings').data('channel');
        const blockIdx = $wfBlock.index();
        
        if (blockIdx < 0 || blockIdx >= $parent.children().length - 1) {
            console.log("Invalid index");
            return;
        }
        
        let $lowerChild = $($parent.children()[blockIdx + 1]);
        $wfBlock.insertAfter($lowerChild);
          
        await eel.py_swap_wf_blocks(tabId, channel, blockIdx, blockIdx+1)();

        await refresh_wf_preview(tabId);
    });

    // Upload waveform
    $('#tab-content').on('click', '.configure-devices', async function() {
        const tabId = get_enclosing_tab_id($(this));
        let success = await eel.py_send_waveform(tabId)();
        if (success) { // Apply some styles to the tab that has been sent
            $('.configure-devices').removeClass('btn-success')
            $(this).addClass('btn-success')

            $('a.nav-link').removeClass('configured-devices-tab')
            $(`a[href="#${tabId}"]`).addClass('configured-devices-tab')
        }
    });

});

function get_enclosing_tab_id($elem) {
    return $elem.closest('.tab-pane').attr('id');
};

async function refresh_wf_preview(tabId) {
    let data = await eel.py_get_wf_skeleton(tabId)();

    let layout = {
        title: {
            text: 'Waveform Preview',
        },
        font: {
            color: '#eee'
        },
        xaxis: {
            title: 'time (s)',
            color: '#eee',
            tickfont: {
                size: 14
            }
        },
        yaxis: {
            title: 'AWG output (V)',
            color: '#eee',
            tickfont: {
                size: 14
            }
        },
        legend: {
            x: 1,
            y: 1,
            xanchor: 'right',
            yanchor: 'top'
        },
        margin: {
            l: 50,
            r: 50,
            b: 50,
            t: 50
        },
        pad: 10,
        autosize: true,
        paper_bgcolor: '#282828',
        plot_bgcolor: '#333'
    };

    let config = {
        responsive: true
    }
    
    Plotly.newPlot($(`#${tabId} .plot-container`)[0], data, layout, config);
}

function add_wf_block(tabId, channel, wfType) {
    const $newBlock = $(`<div class="waveform-block" data-wftype=${wfType}></div>`)
    $(`#${tabId}`).find(`.awg-settings.channel-${channel} .waveform-block-wrapper`).append($newBlock)
    $newBlock.load('waveform-block.html', function() {
        $newBlock.find('.type-waveform-block').text(
            $(`#${tabId} .channel-${channel} option[value="${wfType}"]`).text()
        );
    }); // the things in this function occur AFTER the loading has finished.
}