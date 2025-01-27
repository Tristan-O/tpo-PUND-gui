$(document).ready(function() {
    $('#connect-btn').click(function() {
        eel.py_connect();
    });

    $('#upload-btn').click(function() {
        eel.py_upload();
    });
    
    $('#trigger-btn').click(function() {
        eel.py_trigger();
    });

    $('.close-popup-btn').click(function() {
        $('.popup').css('display', 'none');
    })
});
