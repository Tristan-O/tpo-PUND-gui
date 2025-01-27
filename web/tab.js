let tabCount = 0;

$(document).ready(function() {
    // Add new tab
    $('#add-tab').click(function() {
        const tabName = prompt('Enter a name for the new tab:');
        if (!tabName) return;

        tabCount++;
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
            $(`#${newTabId} .tab-number`).text(tabCount);
            attachDropdownHandler(`#${newTabId} .tab-content-wrapper`);
            attachCloseHandler(newTabId);
        });

        eel.py_new_tab(newTabId, tabName)

        // Activate new tab
        $(`a[href="#${newTabId}"]`).tab('show');
    });

    // Function to attach close button handler
    function attachCloseHandler(tabId) {
        $(`a[href="#${tabId}"]`).find('.close-tab-btn').click(function() {
            closeTab(tabId);
        });
    }

    // Function to close tab
    function closeTab(tabId) {
        // Remove the tab and its content
        $(`a[href="#${tabId}"]`).closest('li').remove();
        $(`#${tabId}`).remove();
        eel.py_close_tab(tabId)

        // Update tab numbers for remaining tabs
        // updateTabNumbers();
    }

    // Function to update tab numbers
    // function updateTabNumbers() {
    //     let currentTab = 1;
    //     $('#tab-list .nav-link:not(#add-tab)').each(function() {
    //         const tabHref = $(this).attr('href').substring(1); // Remove #
    //         $(`#${tabHref} .tab-number`).text(currentTab);
    //         currentTab++;
    //     });

    //     tabCount = currentTab - 1;
    // }

    // Function to attach dropdown handler
    function attachDropdownHandler(tabContentSelector) {
        $(tabContentSelector).find('select').change(function() {
            const selectedOption = $(this).val();
            const channel = $(this).data('channel');
            if (selectedOption == 'pund') {
                addWaveformBlockToChannel(
                    $(this).parent().parent().find('.waveform-block-wrapper'),
                    'PUND');
                $(this).val('none');
                // $('#design-pund').css('display', 'flex'); // only show this when edit clicked
            } else {
                addWaveformBlockToChannel(
                    $(this).parent().parent().find('.waveform-block-wrapper'),
                    selectedOption);
                $(this).val('none');
            }
        });
    }

    // Function to add element to the channel box
    function addWaveformBlockToChannel(waveformBlock, waveformType) {
        waveformBlock.append('<div id="temporary-id-waveform-block" class="waveform-block"></div>') // make a div with a temporary id
        $('#temporary-id-waveform-block').load('waveform-block.html', function() {
            $('#temporary-id-label').text(waveformType);
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
                    console.log(event.target.classList)
                    console.log("clicked...?")
                }
                // TODO Update template WF
            });
            $('#temporary-id-waveform-block').attr('id',''); // clear the id
        }); // the things in this function occur AFTER the loading has finished.
    }
});
