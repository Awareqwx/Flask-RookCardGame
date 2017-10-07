$(document).ready(function(){
    followCards();
    text = "";
    $("#played").each(function(i){
        text += "<input type='hidden' name='card' value='" + i + "'>"
    });
    $("#cardlist").html(text)
    $("#hand .follow").hover(function(){
        $(this).css("border-color", "lightblue");
    }, function(){
        $(this).css("border-color", "black");
    });
    $("#hand .follow").click(function(){
        $(this).data("selected", true);
        $(".card").each(function(i){
            if($(this).data("selected"))
            {
                $("#selectedCard").html("<input type='hidden' name='card' value='" + i + "'>")
            }
        });
        $.ajax({
            url: '/game/trick',
            data: $('#trickform').serialize(),
            type: 'POST',
            success: function(){
                location.href="/game/next"
            }
        });
    });
});

function followCards()
{
    if($("#played .card").length == 0)
    {
        $("#hand .card").each(function(){
            $(this).addClass("follow")
        })
    }
    else
    {
        $("#hand .card").each(function(i){

            if($(this).hasClass($("#follow").val()))
            {
                $(this).addClass("follow")
            }
            else
            {
                $(this).css("border-color", "red")
            }
        });
        if($(".follow").length === 0)
        {
            $("#hand .card").each(function(){
                $(this).addClass("follow")
                $(this).css("border-color", "black")
            })
        }
    }
}