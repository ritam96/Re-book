$(document).ready(function() {
    $("#loginModal").modal();
    $("#registerModal").modal()
})

$('#bookCover').click(function(){
    $('#bookDetailsForm').submit()
})

$('#acceptTradeBtn').click(function() {
    $('#tradeForm').submit()
})
