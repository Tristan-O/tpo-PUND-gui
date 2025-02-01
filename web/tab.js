$(document).ready(function() {

    // Close tab
    // All .close-tab-btns will execute this when clicked, even if they are dynamically created
    $('#tab-list').on('click', '.close-tab-btn', function() {
        const tabSelector = $(this).parent().attr('href');
        const thisIdx = $(this).closest('li').index();
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
            $wrapper = $(this).parent().find('.waveform-block-wrapper')
            const parent_py_id = $wrapper.data('py_id');

            console.log('.waveform-block-adder clicked, parent_py_id = ', parent_py_id);

            new_py_id = await eel.py_new_wf_block(parent_py_id, wfType)();

            add_wf_block($wrapper, new_py_id, wfType)

            $(this).val(''); // reset selector

            await refresh_wf_preview($(this).closest('[data-pyclassname="AWGSettings"]'));
        }
    });


    // Delete waveform block
    $('#tab-content').on('click', '.waveform-block i.delete-waveform-block', async function() {
        console.log("delete clicked!");

        const $wfBlock = $(this).closest('.waveform-block');
        const $awg = $wfBlock.closest('[data-pyclassname="AWGSettings"]');
        
        await eel.py_delete_element($wfBlock.data('py_id'))();
        
        await refresh_wf_preview($awg);
        $wfBlock.remove();
    });


    // Edit waveform block
    $('#tab-content').on('click', '.waveform-block i.edit-waveform-block', async function() {
        console.log("edit clicked!");

        const $wfBlock = $(this).closest('.waveform-block');
        const $awg = $wfBlock.closest('[data-pyclassname="AWGSettings"]');
        const block_py_id = $wfBlock.data('py_id');

        await eel.py_update_frontend(block_py_id)(); // just to make sure this is updated

        let popup = $(` <div class="popup">
                            <div class="popup-content">
                                <form>

                                </form>
                            </div>
                        </div>`);
        $.each($wfBlock.data(), function(key, value) {
            if (key != 'pyclassname' && key != 'py_id') {// don't let users edit this parameters
                console.log(key, ': ', value);
                popup.find('form').append( $(
                    `<div class="form-group">
                        <label>${key}</label>
                        <input class="form-control waveform-parameter" type="number" name="${key}" value=${value}>
                    </div>`
                ));
            }
        });

        const confirmbtn = $(`<button class="btn btn-primary">Confirm</button>`)
        popup.find('.popup-content').append( $(`
            <div class="button-group">
            </div>`).append(confirmbtn)
        );
        confirmbtn.on('click', async function() {
            $.each(popup.find('input'), function(idx, elem) {
                $wfBlock.data($(elem).attr('name'), $(elem).val());
            });
            await eel.py_update_backend(block_py_id, $wfBlock.data())();
            await refresh_wf_preview($awg);
            popup.css('display', 'none');
            popup.remove();
        })

        popup.insertAfter($('#popup-zone'))
        popup.css('display', 'flex');
    });


    // Move-up waveform block
    $('#tab-content').on('click', '.waveform-block i.move-up-waveform-block', async function() {
        console.log("move-up clicked!");

        const $wfBlock = $(this).closest('.waveform-block');
        const $awg = $wfBlock.closest('[data-pyclassname="AWGSettings"]');
        const $parent = $wfBlock.parent(); // this should be a CollectionTemplateWF
        const blockIdx = $wfBlock.index();
        const child_py_id = $wfBlock.data('py_id')
        const parent_py_id = $parent.data('py_id')
        
        if (blockIdx < 1 || blockIdx >= $parent.children().length) {
            console.log("Invalid index");
            return;
        }
        
        let $upperChild = $($parent.children()[blockIdx - 1]);
        $wfBlock.insertBefore($upperChild);

        await eel.py_move_child_elem(parent_py_id, child_py_id, +1)();

        await refresh_wf_preview($awg);
    });

    // Move-up waveform block
    $('#tab-content').on('click', '.waveform-block i.move-down-waveform-block', async function() {
        console.log("move-down clicked!");
        
        const $wfBlock = $(this).closest('.waveform-block');
        const $awg = $wfBlock.closest('[data-pyclassname="AWGSettings"]');
        const $parent = $wfBlock.parent(); // this should be a CollectionTemplateWF
        const blockIdx = $wfBlock.index();
        const child_py_id = $wfBlock.data('py_id')
        const parent_py_id = $parent.data('py_id')

        if (blockIdx < 0 || blockIdx >= $parent.children().length - 1) {
            console.log("Invalid index");
            return;
        }
        
        let $lowerChild = $($parent.children()[blockIdx + 1]);
        $wfBlock.insertAfter($lowerChild);
          
        await eel.py_move_child_elem(parent_py_id, child_py_id, -1)();

        await refresh_wf_preview($awg);
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

    // Elements that have the data-pyparam attribute update the closest div above them that tracks a pyclass
    $('#tab-content').on('input', '[data-pyparam]', function() {
        const param_name = $(this).data('pyparam');
        const new_param_value = $(this).val()
        console.log('Updating', param_name, 'to', new_param_value);
        console.log('Old value', $(this).closest(`[data-pyclassname]`).data(param_name));
        $(this).closest(`[data-pyclassname]`).data(param_name, new_param_value);
        console.log('Check new value took hold:', $(this).closest(`[data-pyclassname]`).data(param_name));
    });

});

function get_enclosing_tab_id($elem) {
    return $elem.closest('.tab-pane').attr('id');
};

async function refresh_wf_preview($awgsettings) {
    let data = await eel.py_get_wf_skeleton($awgsettings.data('py_id'))();

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
    Plotly.newPlot($awgsettings.parent().find('.plot-container')[0], data, layout, config);
};

function add_wf_block($wrapper, new_py_id, wfType) {
    console.log('In add_wf_block, new_py_id = ', new_py_id);
    const $newBlock = $(`<div class="waveform-block" data-py_id="${new_py_id}" data-pyclassname=${wfType}></div>`);
    $wrapper.append($newBlock);
    $newBlock.load('waveform-block.html', async function() {
        $newBlock.find('.type-waveform-block').text(
            $wrapper.parent().find(`option[value="${wfType}"]`).text()
        );
        await eel.py_update_frontend(new_py_id); // python has already created the new wf block with the given py_id in the backend. 
                                // Now we're asking python to fill in the relevant class parameters into this element
    }); // the things in this function occur AFTER the loading has finished.
};
