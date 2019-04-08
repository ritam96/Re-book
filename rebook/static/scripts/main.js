$(document).ready(function(){
    $('#editModal').toggle()
})

$('#bookCover').click(function(){
    $('#bookDetailsForm').submit()
})

$('#acceptTradeBtn').click(function() {
    $('#tradeForm').submit()
})

function show(){
    if($('#sell').is(':checked')) {
    $('#selling').show()
    } else {
    $('#selling').hide()

    }
}
