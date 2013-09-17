//IMPORTANT!!
// Set two variables before using the singleton from this script
//CHECK_STATUS_URL
//&
//PROBLEM_GROUP_URL

//Modal Usun problem
$("#modal-submit").click(function(e) {
    e.preventDefault();
    $("#modal-form").submit();
});
var EditHandler = function(e) {
    e.preventDefault();
    $('#modal-group-form').submit();
};

//Singleton representing group modal
var GroupModal = (function() {
    //Private
    var $modal = $('#modal-group');
    var $console = $('#progress-console ul');
    var $cancelButton = $('#modal-group-cancel');
    var $successButton = $('#modal-group-success');
    var $progressbar = $('#progressbar');
    var $form = $('#modal-group-form');

    var progressUpdateMethodHandler = null;
    var consoleLogMessageTemplate = '<li><p>#</p></li>';

    var ResetProgressBar = function() {
        $progressbar.html('');
    };
    var UpdateProgressBar = function(style, width) {
        if (style)
            style = 'bar-' + style;//Bottle neck - no data validation!
        var progressBarHtml = '<div class="bar ' + style +'" style="width: ' + width + '%;"></div>';
        $progressbar.append(progressBarHtml);
    };
    var ReturnProgress = function() {
        var sum = 0;
        $('#progressbar div').each(function() { sum += parseInt($(this).css('width')) });
        return sum;
    };
    //Method writes message to the modal body section - feedback for the user
    var Log = function(msg) {
        $console.append(consoleLogMessageTemplate.replace('#', msg));
    };
    var ClearConsole = function() {
        $console.html('');
    };

    var CancelClickHandler = function(e) {
        e.preventDefault();
        clearInterval(progressUpdateMethodHandler);
        $successButton.addClass('disabled');
    };
    var SuccessClickHandler = function(e) {
        if ( !$successButton.hasClass('disabled') ) {
            e.preventDefault();
            $cancelButton.attr('data-dismiss', 'modal');//Activate hiding modal window
            $cancelButton.bind('click', CancelClickHandler);
            $form.submit();
        }
    };
    var ProgressBarUpdate = function() {
        progressUpdateMethodHandler = setInterval(function() {
            $.ajax({
                    url: CHECK_STATUS_URL,//Remember to set this CONSTANT before any use of the object
                    type: "POST",
                    dataType: "json"
            }).done(HandleProgressChange);
        }, 500);
    };
    var HandleProgressChange = function(result) {
        if (result) {
            UpdateProgressBar(result.style, result.width);
            var progress = ReturnProgress();
            if ( result.style == 'danger' || progress >= 100 )//Error or the end
                clearInterval(progressUpdateMethodHandler);
            if ( progress >= 100 && result.style != 'danger' ) {//The end and success
                clearInterval(progressUpdateMethodHandler);
                $successButton.removeClass('disabled');
                $('#edit').bind('click', EditHandler);//Global Edit button
                $('#edit').removeClass('disabled');
                $cancelButton.addClass('disabled');
                $cancelButton.attr('data-dismiss', '');
                $cancelButton.unbind('click');
            }
        }
    };

    var RequestDoneHandler = function(result) {
        Log(result);
        ProgressBarUpdate();
    };
    var RequestFailHandler = function(result) {
        Log('ERROR');
    };

    return {
    //Public
        Init : function() {
            $cancelButton.bind('click', CancelClickHandler);
            $successButton.bind('click', SuccessClickHandler);
            $modal.on('shown', function(e) {
                e.preventDefault();
                ResetProgressBar();
                ClearConsole();
                $cancelButton.removeClass('disabled');
                $cancelButton.bind('click', CancelClickHandler);
                var request = $.ajax({
                    url: PROBLEM_GROUP_URL,
                    type: "POST"
                });
                request.done(RequestDoneHandler);
                request.fail(RequestFailHandler);
            });
        }
    };
})();